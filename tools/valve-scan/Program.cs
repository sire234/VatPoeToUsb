// valve-scan: finds PoE-USB-HID bridges via mDNS (_poehid._tcp), lists the VAT valves connected
// to them and reads a few parameters (read-only, plus the W1 number format writes of the legacy
// CPA). Commands and value types: firmware/src/valve-commands.md.
//
//   valve-scan                 browse via mDNS (3 s)
//   valve-scan 192.168.1.200   skip mDNS, use this bridge address
using System.Globalization;
using System.Net;
using ValveScan;

var bridges = new List<BridgeInfo>();
if (args.Length > 0 && IPAddress.TryParse(args[0], out var direct))
{
    bridges.Add(new BridgeInfo("(manual)", args[0], direct, 5000));
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
        return 1;
    }
}

if (bridges.Count == 0)
{
    Console.WriteLine("No bridge found. Tip: valve-scan <ip>");
    return 1;
}

foreach (var bridge in bridges)
{
    Console.WriteLine();
    Console.WriteLine($"Bridge {bridge.Instance}");
    Console.WriteLine($"  {bridge.Host}  {bridge.Address}:{bridge.Port}");
    try
    {
        using var client = new BridgeClient(bridge.Address, bridge.Port, TimeSpan.FromSeconds(3));
        Console.WriteLine($"  {client.Banner}");

        var valves = client.ListValves();
        Console.WriteLine($"  Valves: {(valves.Count == 0 ? "none" : string.Join(", ", valves.Select(v => $"v{v}")))}");

        foreach (int addr in valves)
            ReadValve(client, addr);
    }
    catch (Exception e)
    {
        Console.WriteLine($"  Error: {e.Message}");
    }
}
return 0;

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

sealed record Parameter(string Name, string Id, ParamType Type, Dictionary<int, string>? Names = null, string Unit = "");

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
        new("Serial Number",       "0F10010000", ParamType.Text),
        new("Firmware",            "0F10030200", ParamType.Text),
        new("Device Series",       "0F10020100", ParamType.U16, Series),
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
