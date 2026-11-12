// valve-scan: finds PoE-USB-HID bridges via mDNS (_poehid._tcp), lists the VAT valves connected
// to them and reads a few parameters (read-only, plus the W1 number format writes of the legacy
// CPA). Commands and value types: firmware/src/valve-commands.md.
//
//   valve-scan                 browse via mDNS (3 s)
//   valve-scan 192.168.1.200   skip mDNS, use this bridge address
//   --no-wait                  do not wait for Enter at the end (for scripts)
//   --verbose                  debug output: mDNS packets and every TCP line, with timestamps
//   --endurance [--duration s] endurance test: read all parameters (and every 50 rounds the full
//                              tree) of all valves in a loop, stop with Enter / Ctrl+C
using System.Globalization;
using System.Net;
using ValveScan;

Log.Verbose = args.Contains("--verbose") || args.Contains("-v");
bool wait = !args.Contains("--no-wait") && !Console.IsInputRedirected;
bool endurance = args.Contains("--endurance") || args.Contains("--dauertest");
TimeSpan? duration = null;
int durationIndex = Array.IndexOf(args, "--duration");
if (durationIndex >= 0 && durationIndex + 1 < args.Length && double.TryParse(args[durationIndex + 1], CultureInfo.InvariantCulture, out var seconds))
    duration = TimeSpan.FromSeconds(seconds);
string? ip = args.Where((a, i) => !a.StartsWith("-") && (i == 0 || args[i - 1] != "--duration")).FirstOrDefault();
int exitCode = endurance ? RunEndurance(ip, duration) : Scan(ip);
if (wait)
{
    Console.WriteLine();
    Console.Write("Press Enter to exit ...");
    Console.ReadLine();
}
return exitCode;

static List<BridgeInfo>? FindBridges(string? ip)
{
    var bridges = new List<BridgeInfo>();
    if (ip != null && IPAddress.TryParse(ip, out var direct))
    {
        bridges.Add(new BridgeInfo("(manual)", ip, direct, 5000));
    }
    else
    {
        Console.WriteLine("Searching bridges via mDNS (_poehid._tcp.local) ...");
        try
        {
            bridges = Mdns.Browse(TimeSpan.FromSeconds(3));
        }
        catch (Exception e)
        {
            Console.WriteLine($"mDNS failed: {e.Message}");
            Console.WriteLine("Tip: valve-scan <ip>");
            return null;
        }
    }

    if (bridges.Count == 0)
    {
        Console.WriteLine("No bridge found. Tip: valve-scan <ip>");
        return null;
    }
    return bridges;
}

static int RunEndurance(string? ip, TimeSpan? duration)
{
    var bridges = FindBridges(ip);
    if (bridges == null)
        return 1;
    var bridge = bridges[0];
    if (bridges.Count > 1)
        Console.WriteLine($"{bridges.Count} bridges found, testing the first one ({bridge.Host}). Choose another with valve-scan <ip> --endurance.");
    Console.WriteLine($"Bridge {bridge.Instance}  {bridge.Address}:{bridge.Port}");
    try
    {
        using var client = new BridgeClient(bridge.Address, bridge.Port, TimeSpan.FromSeconds(3));
        Console.WriteLine($"  {client.Banner}");
        if (Log.Verbose)
            client.EnableFirmwareDebug();
        var valves = client.ListValves();
        if (valves.Count == 0)
        {
            Console.WriteLine("  No valves connected.");
            return 1;
        }
        return new Endurance(client, valves, duration).Run();
    }
    catch (Exception e)
    {
        Console.WriteLine($"  Error: {e.Message}");
        return 1;
    }
}

static int Scan(string? ip)
{
    var bridges = FindBridges(ip);
    if (bridges == null)
        return 1;

    foreach (var bridge in bridges)
    {
        Console.WriteLine();
        Console.WriteLine($"Bridge {bridge.Instance}");
        Console.WriteLine($"  {bridge.Host}  {bridge.Address}:{bridge.Port}");
        try
        {
            using var client = new BridgeClient(bridge.Address, bridge.Port, TimeSpan.FromSeconds(3));
            Console.WriteLine($"  {client.Banner}");
            if (Log.Verbose)
                client.EnableFirmwareDebug();

            var valves = client.ListValves();
            Console.WriteLine($"  Valves: {(valves.Count == 0 ? "none" : string.Join(", ", valves.Select(v => $"v{v}")))}");

            foreach (int addr in valves)
                ReadValve(client, addr);

            if (Log.Verbose)
                client.Drain(TimeSpan.FromMilliseconds(300));   // last firmware debug lines
        }
        catch (Exception e)
        {
            Console.WriteLine($"  Error: {e.Message}");
        }
    }
    return 0;
}

static void ReadValve(BridgeClient client, int addr)
{
    Console.WriteLine();
    Console.WriteLine($"  Valve v{addr}");

    // W1: number formats to hex (integer: hex fixed length, float: hex fixed length), as legacy CPA does on connect
    client.ValveCommand(addr, "p:01060201010003");
    client.ValveCommand(addr, "p:01060201020002");

    foreach (var p in Parameters.All)
    {
        string value;
        try
        {
            string reply = client.ValveCommand(addr, "p:0B" + p.Id);
            value = Parameters.Decode(p, reply);
        }
        catch (Exception e)
        {
            value = "(" + e.Message + ")";
        }
        Console.WriteLine($"    {p.Name,-24} {value}");
    }
}

enum ParamType { Text, U8Enum, U16, U32Hex, Float }

// Static: must not change while the valve runs (checked by the endurance test)
sealed record Parameter(string Name, string Id, ParamType Type, Dictionary<int, string>? Names = null, string Unit = "", bool Static = false);

static class Parameters
{
    private static readonly Dictionary<int, string> ControlModes = new()
    {
        [0] = "Init", [2] = "Position", [3] = "Close", [4] = "Open", [6] = "Hold", [14] = "Error",
    };
    private static readonly Dictionary<int, string> AccessModes = new()
    {
        [0] = "Local", [1] = "Remote", [2] = "Remote Locked",
    };
    private static readonly Dictionary<int, string> Series = new() { [1] = "Simulation" };

    // ID = parameter ID (8 hex) + index (2 hex), see valve-commands.md
    public static readonly Parameter[] All =
    {
        new("Serial Number",       "0F10010000", ParamType.Text, Static: true),
        new("Firmware",            "0F10030200", ParamType.Text, Static: true),
        new("Device Series",       "0F10020100", ParamType.U16, Series, Static: true),
        new("Control Mode",        "0F02000000", ParamType.U8Enum, ControlModes),
        new("Access Mode",         "0F0B000000", ParamType.U8Enum, AccessModes),
        new("Error Number",        "0F30060000", ParamType.U16),
        new("Error Code",          "0F30070000", ParamType.U16),
        new("Warning Bitmap",      "0F30010000", ParamType.U32Hex),
        new("Actual Position",     "1101000000", ParamType.Float, Unit: " %"),
        new("Target Position",     "1102000000", ParamType.Float, Unit: " %"),
        new("Position Ctrl Speed", "1103000000", ParamType.Float),
        new("Actual Pressure",     "2006010000", ParamType.Float),
    };

    /// <summary>Reply "p:" + error (2) + service (2) + ID (8) + index (2) + value.</summary>
    public static string Decode(Parameter p, string reply)
    {
        if (!reply.StartsWith("p:") || reply.Length < 16)
            return "(unexpected reply: " + reply + ")";
        string error = reply.Substring(2, 2);
        if (error != "00")
            return $"(valve error 0x{error})";
        string v = reply[16..];

        switch (p.Type)
        {
            case ParamType.Text:
                return v;
            case ParamType.U8Enum:
            case ParamType.U16:
                {
                    int n = int.Parse(v, NumberStyles.HexNumber);
                    if (p.Type == ParamType.U8Enum && v.Length == 2)
                        n = (sbyte)n;
                    return p.Names != null && p.Names.TryGetValue(n, out var name) ? $"{n} ({name})" : n.ToString();
                }
            case ParamType.U32Hex:
                {
                    uint bits = uint.Parse(v, NumberStyles.HexNumber);
                    return bits == 0 ? "0x00000000 (none)" : $"0x{bits:X8}";
                }
            case ParamType.Float:
                {
                    uint bits = uint.Parse(v.PadLeft(8, '0'), NumberStyles.HexNumber);
                    float f = MathF.Round(BitConverter.UInt32BitsToSingle(bits), 3);
                    if (f == 0f)
                        f = 0f;                     // tiny negative values: show 0, not -0
                    return f.ToString("0.###", CultureInfo.InvariantCulture) + p.Unit;
                }
            default:
                return v;
        }
    }
}
