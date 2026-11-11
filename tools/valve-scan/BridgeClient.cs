using System.Net;
using System.Net.Sockets;
using System.Text;

namespace ValveScan;

/// <summary>
/// Line-based TCP client for the bridge (port 5000). The bridge also sends unrelated lines
/// (keyboard text, "#HID ..." events), so every request waits for the line it expects.
/// </summary>
public sealed class BridgeClient : IDisposable
{
    private readonly TcpClient client = new();
    private readonly NetworkStream stream;
    private readonly StringBuilder pending = new();
    private readonly byte[] buffer = new byte[8192];

    public BridgeClient(IPAddress address, int port, TimeSpan connectTimeout)
    {
        if (!client.ConnectAsync(address, port).Wait(connectTimeout))
            throw new TimeoutException($"No TCP connection to {address}:{port}.");
        stream = client.GetStream();
        Banner = ReadLine(l => l.StartsWith("#STATUS"), TimeSpan.FromSeconds(2)) ?? "";
    }

    /// <summary>The "#STATUS ..." line the bridge sends on connect.</summary>
    public string Banner { get; }

    /// <summary>Addresses of the connected valves ("#VALVES v1 v2").</summary>
    public List<int> ListValves()
    {
        Send("valves");
        string? line = ReadLine(l => l.StartsWith("#VALVES"), TimeSpan.FromSeconds(2));
        if (line == null)
            throw new IOException("The bridge did not answer 'valves' (old firmware?).");
        return line.Split(' ', StringSplitOptions.RemoveEmptyEntries).Skip(1)
            .Select(v => int.Parse(v.TrimStart('v'))).ToList();
    }

    /// <summary>Sends a text command to valve <paramref name="addr"/>; returns the reply without "#V&lt;addr&gt; ".</summary>
    public string ValveCommand(int addr, string command)
    {
        Send($"v{addr} {command}");
        string prefix = $"#V{addr} ";
        string? line = ReadLine(l => l.StartsWith(prefix), TimeSpan.FromSeconds(3));
        if (line == null)
            throw new TimeoutException($"No reply from the bridge for v{addr} {command}.");
        string reply = line[prefix.Length..];
        if (reply.StartsWith("ERR"))
            throw new IOException($"v{addr} {command}: {reply}");
        return reply;
    }

    private void Send(string line)
    {
        byte[] bytes = Encoding.ASCII.GetBytes(line + "\n");
        stream.Write(bytes, 0, bytes.Length);
    }

    private string? ReadLine(Func<string, bool> wanted, TimeSpan timeout)
    {
        var end = DateTime.UtcNow + timeout;
        while (true)
        {
            string text = pending.ToString();
            int nl;
            while ((nl = text.IndexOf('\n')) >= 0)
            {
                string line = text[..nl].TrimEnd('\r');
                text = text[(nl + 1)..];
                pending.Clear().Append(text);
                if (wanted(line))
                    return line;
            }

            var left = end - DateTime.UtcNow;
            if (left <= TimeSpan.Zero)
                return null;
            stream.ReadTimeout = (int)Math.Max(1, left.TotalMilliseconds);
            int n;
            try { n = stream.Read(buffer, 0, buffer.Length); }
            catch (IOException) { return null; }   // read timeout
            if (n == 0)
                throw new IOException("The bridge closed the connection.");
            pending.Append(Encoding.ASCII.GetString(buffer, 0, n));
        }
    }

    public void Dispose() => client.Dispose();
}
