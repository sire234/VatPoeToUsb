using System.Net;
using System.Net.Sockets;
using System.Text;

namespace ValveScan;

/// <summary>An "#V&lt;addr&gt; ERR ..." reply of the bridge (timeout, busy, blocked, no valve, ...).</summary>
public sealed class BridgeErrorException(int addr, string command, string reason)
    : IOException($"v{addr} {command}: ERR {reason}")
{
    public string Reason { get; } = reason;
}

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
        Log.Debug($"TCP: connecting to {address}:{port}");
        try
        {
            if (!client.ConnectAsync(address, port).Wait(connectTimeout))
                throw new TimeoutException($"No TCP connection to {address}:{port} within {connectTimeout.TotalSeconds:0} s.");
        }
        catch (AggregateException e) when (e.InnerException != null)
        {
            // e.g. "connection refused": the bridge accepts only one client at a time
            throw new IOException($"No TCP connection to {address}:{port}: {e.InnerException.Message}", e.InnerException);
        }
        Log.Debug("TCP: connected");
        stream = client.GetStream();
        Banner = ReadLine(l => l.StartsWith("#STATUS"), TimeSpan.FromSeconds(2)) ?? "";
    }

    /// <summary>The "#STATUS ..." line the bridge sends on connect.</summary>
    public string Banner { get; }

    /// <summary>
    /// Shows the firmware debug history ("log") and switches on live firmware debug output
    /// ("debug on"). The lines are printed by <see cref="Log"/> as they arrive (--verbose only).
    /// </summary>
    public void EnableFirmwareDebug()
    {
        Send("log");
        if (ReadLine(l => l == "#LOG end", TimeSpan.FromSeconds(3)) == null)
            Log.Debug("firmware: no debug log (old firmware?)");
        Send("debug on");
        ReadLine(l => l.StartsWith("#OK debug") || l.StartsWith("#ERR"), TimeSpan.FromSeconds(2));
    }

    /// <summary>Reads and logs the lines that still arrive within <paramref name="time"/>.</summary>
    public void Drain(TimeSpan time) => ReadLine(_ => false, time, quietTimeout: true);

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
            throw new BridgeErrorException(addr, command, reply[3..].Trim());
        return reply;
    }

    /// <summary>
    /// Multi-part g: command (e.g. "g:1E18"): first "&lt;cmd&gt;START", then "&lt;cmd&gt;" until the reply ends
    /// with RS "EnD" RS. Returns the joined content without the command headers and the number of parts.
    /// </summary>
    public (string Content, int Parts) ValveMultiPart(int addr, string command, int maxParts = 1000)
    {
        var content = new StringBuilder();
        for (int part = 0; part < maxParts; part++)
        {
            string reply = ValveCommand(addr, part == 0 ? command + "START" : command);
            if (!reply.StartsWith(command, StringComparison.OrdinalIgnoreCase))
                throw new IOException($"v{addr} {command}: unexpected reply \"{Log.Visible(reply[..Math.Min(40, reply.Length)])}\"");
            content.Append(reply, command.Length, reply.Length - command.Length);
            if (reply.EndsWith("\u001eEnD\u001e"))
                return (content.ToString(), part + 1);
        }
        throw new IOException($"v{addr} {command}: no end marker after {maxParts} parts");
    }
    private void Send(string line)
    {
        byte[] bytes = Encoding.ASCII.GetBytes(line + "\n");
        stream.Write(bytes, 0, bytes.Length);
        Log.Debug($"TCP >> {line}");
    }

    private string? ReadLine(Func<string, bool> wanted, TimeSpan timeout, bool quietTimeout = false)
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
                bool match = wanted(line);
                if (line.StartsWith("#DBG "))
                    Log.Firmware(line[5..], live: true);
                else if (line.StartsWith("#LOG ") && line != "#LOG end")
                    Log.Firmware(line[5..], live: false);
                else
                    Log.Debug($"TCP << {Log.Visible(line)}{(match ? "" : "   (ignored)")}");
                if (match)
                    return line;
            }

            var left = end - DateTime.UtcNow;
            if (left <= TimeSpan.Zero)
            {
                if (!quietTimeout)
                    Log.Debug($"TCP: timeout after {timeout.TotalSeconds:0.0} s");
                return null;
            }
            stream.ReadTimeout = (int)Math.Max(1, left.TotalMilliseconds);
            int n;
            try { n = stream.Read(buffer, 0, buffer.Length); }
            catch (IOException e) when (e.InnerException is SocketException { SocketErrorCode: SocketError.TimedOut })
            {
                continue;                           // read timeout: the loop checks the deadline
            }
            if (n == 0)
                throw new IOException("The bridge closed the connection.");
            pending.Append(Encoding.ASCII.GetString(buffer, 0, n));
        }
    }

    public void Dispose() => client.Dispose();
}
