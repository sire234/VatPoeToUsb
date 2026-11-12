namespace ValveScan;

/// <summary>Debug output for --verbose: time since start + message, in grey.</summary>
public static class Log
{
    private static readonly DateTime Start = DateTime.Now;

    public static bool Verbose { get; set; }

    public static void Debug(string message)
    {
        if (!Verbose)
            return;
        var color = Console.ForegroundColor;
        Console.ForegroundColor = ConsoleColor.DarkGray;
        Console.WriteLine($"[{(DateTime.Now - Start).TotalSeconds,6:0.000}] {message}");
        Console.ForegroundColor = color;
    }

    /// <summary>
    /// A firmware debug line "&lt;uptime s&gt; &lt;text&gt;": "FW" for live output, "FW-LOG" for the history
    /// from before this connection. The uptime is the bridge clock, not the PC clock.
    /// </summary>
    public static void Firmware(string line, bool live)
    {
        if (!Verbose)
            return;
        int space = line.IndexOf(' ');
        string uptime = space > 0 ? line[..space] : "";
        string text = space > 0 ? line[(space + 1)..] : line;
        var color = Console.ForegroundColor;
        Console.ForegroundColor = live ? ConsoleColor.DarkCyan : ConsoleColor.DarkYellow;
        Console.WriteLine($"[{(DateTime.Now - Start).TotalSeconds,6:0.000}] {(live ? "FW    " : "FW-LOG")} up {uptime,9} s  {text}");
        Console.ForegroundColor = color;
    }

    /// <summary>Makes control characters of valve replies visible (RS = 0x1E).</summary>
    public static string Visible(string s) =>
        s.Replace("\u001e", "<RS>").Replace("\r", "<CR>").Replace("\n", "<LF>");
}
