using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Text;

namespace ValveScan;

/// <summary>A bridge found via DNS-SD: instance name, host name, address and TCP port.</summary>
public sealed record BridgeInfo(string Instance, string Host, IPAddress Address, int Port);

/// <summary>
/// Minimal mDNS / DNS-SD browser (RFC 6762/6763) for "_poehid._tcp.local".
/// The bridge firmware only answers queries from source port 5353 and replies by multicast,
/// so the query is sent from a socket bound to 5353 (shared with the Windows mDNS service).
/// </summary>
public static class Mdns
{
    private const string ServiceType = "_poehid._tcp.local";
    private const ushort TypeA = 1, TypePtr = 12, TypeSrv = 33;
    private static readonly IPAddress Group = IPAddress.Parse("224.0.0.251");
    private const int Port = 5353;

    public static List<BridgeInfo> Browse(TimeSpan duration)
    {
        using var socket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
        socket.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
        socket.Bind(new IPEndPoint(IPAddress.Any, Port));

        var interfaces = LocalIPv4Addresses();
        foreach (var local in interfaces)
        {
            try { socket.SetSocketOption(SocketOptionLevel.IP, SocketOptionName.AddMembership, new MulticastOption(Group, local)); }
            catch (SocketException) { /* interface without multicast */ }
        }

        byte[] query = BuildQuery(ServiceType, TypePtr);
        foreach (var local in interfaces)
        {
            try
            {
                socket.SetSocketOption(SocketOptionLevel.IP, SocketOptionName.MulticastInterface, local.GetAddressBytes());
                socket.SendTo(query, new IPEndPoint(Group, Port));
            }
            catch (SocketException) { /* ignore interfaces that cannot send */ }
        }

        var instances = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var srv = new Dictionary<string, (string Host, int Port)>(StringComparer.OrdinalIgnoreCase);
        var hosts = new Dictionary<string, IPAddress>(StringComparer.OrdinalIgnoreCase);

        var buffer = new byte[9000];
        var end = DateTime.UtcNow + duration;
        while (DateTime.UtcNow < end)
        {
            int waitUs = (int)Math.Max(1, (end - DateTime.UtcNow).TotalMilliseconds) * 1000;
            if (!socket.Poll(waitUs, SelectMode.SelectRead))
                break;
            EndPoint from = new IPEndPoint(IPAddress.Any, 0);
            int n = socket.ReceiveFrom(buffer, ref from);
            try { ParseResponse(buffer.AsSpan(0, n).ToArray(), instances, srv, hosts); }
            catch (Exception) { /* malformed packet of some other device: ignore */ }
        }

        var result = new List<BridgeInfo>();
        foreach (var instance in instances)
        {
            if (!srv.TryGetValue(instance, out var target) || !hosts.TryGetValue(target.Host, out var address))
                continue;
            result.Add(new BridgeInfo(instance, target.Host, address, target.Port));
        }
        return result.OrderBy(b => b.Host).ToList();
    }

    private static List<IPAddress> LocalIPv4Addresses() =>
        NetworkInterface.GetAllNetworkInterfaces()
            .Where(i => i.OperationalStatus == OperationalStatus.Up && i.SupportsMulticast
                        && i.NetworkInterfaceType != NetworkInterfaceType.Loopback)
            .SelectMany(i => i.GetIPProperties().UnicastAddresses)
            .Where(a => a.Address.AddressFamily == AddressFamily.InterNetwork)
            .Select(a => a.Address)
            .ToList();

    private static byte[] BuildQuery(string name, ushort type)
    {
        var q = new List<byte> { 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0 };   // id 0, flags 0, 1 question
        foreach (var label in name.Split('.'))
        {
            var bytes = Encoding.UTF8.GetBytes(label);
            q.Add((byte)bytes.Length);
            q.AddRange(bytes);
        }
        q.Add(0);
        q.AddRange(new byte[] { (byte)(type >> 8), (byte)type, 0, 1 });   // class IN, QM
        return q.ToArray();
    }

    private static void ParseResponse(byte[] msg, HashSet<string> instances,
        Dictionary<string, (string, int)> srv, Dictionary<string, IPAddress> hosts)
    {
        if (msg.Length < 12 || (msg[2] & 0x80) == 0)
            return;                                     // not a response
        int qd = U16(msg, 4), records = U16(msg, 6) + U16(msg, 8) + U16(msg, 10);
        int off = 12;
        for (int i = 0; i < qd; i++)
        {
            ReadName(msg, ref off);
            off += 4;
        }
        for (int i = 0; i < records; i++)
        {
            string name = ReadName(msg, ref off);
            ushort type = U16(msg, off);
            int rdlen = U16(msg, off + 8);
            int rdata = off + 10;
            off = rdata + rdlen;

            if (type == TypePtr && name.Equals(ServiceType, StringComparison.OrdinalIgnoreCase))
            {
                int p = rdata;
                instances.Add(ReadName(msg, ref p));
            }
            else if (type == TypeSrv)
            {
                int p = rdata + 6;                      // priority, weight, port
                srv[name] = (ReadName(msg, ref p), U16(msg, rdata + 4));
            }
            else if (type == TypeA && rdlen == 4)
            {
                hosts[name] = new IPAddress(msg.AsSpan(rdata, 4));
            }
        }
    }

    private static ushort U16(byte[] b, int o) => (ushort)((b[o] << 8) | b[o + 1]);

    private static string ReadName(byte[] msg, ref int off)
    {
        var labels = new List<string>();
        int pos = off;
        bool jumped = false;
        for (int guard = 0; guard < 64; guard++)
        {
            int len = msg[pos];
            if (len == 0)
            {
                pos++;
                break;
            }
            if ((len & 0xC0) == 0xC0)                   // compression pointer
            {
                if (!jumped)
                    off = pos + 2;
                jumped = true;
                pos = ((len & 0x3F) << 8) | msg[pos + 1];
                continue;
            }
            labels.Add(Encoding.UTF8.GetString(msg, pos + 1, len));
            pos += 1 + len;
        }
        if (!jumped)
            off = pos;
        return string.Join('.', labels);
    }
}
