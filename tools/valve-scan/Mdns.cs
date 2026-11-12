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
            try
            {
                socket.SetSocketOption(SocketOptionLevel.IP, SocketOptionName.AddMembership, new MulticastOption(Group, local));
                Log.Debug($"mDNS: joined 224.0.0.251 on {local}");
            }
            catch (SocketException e)
            {
                Log.Debug($"mDNS: cannot join on {local}: {e.Message}");
            }
        }

        void SendQuery(string name, ushort type)
        {
            byte[] query = BuildQuery(name, type);
            foreach (var local in interfaces)
            {
                try
                {
                    socket.SetSocketOption(SocketOptionLevel.IP, SocketOptionName.MulticastInterface, local.GetAddressBytes());
                    socket.SendTo(query, new IPEndPoint(Group, Port));
                    Log.Debug($"mDNS: query {TypeName(type)} {name} via {local}");
                }
                catch (SocketException e)
                {
                    Log.Debug($"mDNS: query {TypeName(type)} {name} via {local} failed: {e.Message}");
                }
            }
        }

        var instances = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var srv = new Dictionary<string, (string Host, int Port)>(StringComparer.OrdinalIgnoreCase);
        var hosts = new Dictionary<string, IPAddress>(StringComparer.OrdinalIgnoreCase);

        // multicast over WLAN loses packets (power save, AP buffering), so the query is repeated
        // (RFC 6762 5.2: increasing intervals); missing SRV/A records are asked for explicitly
        var start = DateTime.UtcNow;
        var end = start + duration;
        var repeats = new Queue<TimeSpan>(new[] { 0.0, 0.5, 1.0, 2.0 }.Select(TimeSpan.FromSeconds));
        var buffer = new byte[9000];
        while (DateTime.UtcNow < end)
        {
            if (repeats.Count > 0 && DateTime.UtcNow - start >= repeats.Peek())
            {
                repeats.Dequeue();
                SendQuery(ServiceType, TypePtr);
                foreach (var instance in instances.Where(i => !srv.ContainsKey(i)))
                    SendQuery(instance, TypeSrv);
                foreach (var host in srv.Values.Select(s => s.Host).Where(h => !hosts.ContainsKey(h)).Distinct())
                    SendQuery(host, TypeA);
            }

            var next = repeats.Count > 0 ? start + repeats.Peek() : end;
            int waitUs = (int)Math.Max(1, (Min(next, end) - DateTime.UtcNow).TotalMilliseconds) * 1000;
            if (!socket.Poll(waitUs, SelectMode.SelectRead))
                continue;
            EndPoint from = new IPEndPoint(IPAddress.Any, 0);
            int n;
            try
            {
                n = socket.ReceiveFrom(buffer, ref from);
            }
            catch (SocketException e)
            {
                // Windows reports e.g. an ICMP "port unreachable" of an earlier send here: skip it
                Log.Debug($"mDNS: receive error {e.SocketErrorCode}, ignored");
                continue;
            }
            try { ParseResponse(buffer.AsSpan(0, n).ToArray(), instances, srv, hosts, from); }
            catch (Exception e) { Log.Debug($"mDNS: {n} bytes from {from} not parsed: {e.Message}"); }
        }
        Log.Debug($"mDNS: done, {instances.Count} instance(s), {srv.Count} SRV, {hosts.Count} A record(s)");

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
        Dictionary<string, (string, int)> srv, Dictionary<string, IPAddress> hosts, EndPoint from)
    {
        if (msg.Length < 12 || (msg[2] & 0x80) == 0)
            return;                                     // not a response (e.g. our own or other queries)
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
                string instance = ReadName(msg, ref p);
                instances.Add(instance);
                Log.Debug($"mDNS: from {from}: PTR {name} -> {instance}");
            }
            else if (type == TypeSrv)
            {
                int p = rdata + 6;                      // priority, weight, port
                srv[name] = (ReadName(msg, ref p), U16(msg, rdata + 4));
                Log.Debug($"mDNS: from {from}: SRV {name} -> {srv[name].Item1}:{srv[name].Item2}");
            }
            else if (type == TypeA && rdlen == 4)
            {
                hosts[name] = new IPAddress(msg.AsSpan(rdata, 4));
                Log.Debug($"mDNS: from {from}: A {name} -> {hosts[name]}");
            }
        }
    }

    private static DateTime Min(DateTime a, DateTime b) => a < b ? a : b;

    private static string TypeName(ushort type) =>
        type switch { TypeA => "A", TypePtr => "PTR", TypeSrv => "SRV", _ => type.ToString() };

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
