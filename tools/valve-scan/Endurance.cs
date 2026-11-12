using System.Diagnostics;
using System.Security.Cryptography;
using System.Text;

namespace ValveScan;

/// <summary>
/// Endurance test: reads all parameters of all valves of one bridge in a loop, without pause, and
/// every <see cref="TreeEvery"/> rounds the full parameter tree (g:1E18, many USB reports per part).
/// Static values (serial number, firmware, series, tree length and hash) must not change; a change
/// counts as a mismatch. Read commands only (plus the W1 writes once at the start).
/// Stops on Enter, Ctrl+C or after the given duration.
/// </summary>
public sealed class Endurance(BridgeClient client, List<int> valves, TimeSpan? duration)
{
    private const int TreeEvery = 50;
    private static readonly TimeSpan StatusEvery = TimeSpan.FromSeconds(5);

    private readonly Dictionary<string, string> reference = new();   // "v1 <param>" -> first value
    private readonly long[] histogram = new long[30001];             // single commands, 0.1 ms steps up to 3 s
    private long latencyCount;
    private double latencySum, latencyMax;
    private readonly Dictionary<string, long> errors = new();        // kind -> count
    private long requests, ok, mismatches, trees, treeParts;
    private double treeMsTotal;

    public int Run()
    {
        bool stop = false;
        Console.CancelKeyPress += (_, e) => { e.Cancel = true; stop = true; };
        bool keys = !Console.IsInputRedirected;

        Console.WriteLine();
        Console.WriteLine($"Endurance test on {string.Join(", ", valves.Select(v => $"v{v}"))}" +
                          (duration is { } d ? $" for {d.TotalSeconds:0} s" : "") +
                          $", full tree every {TreeEvery} rounds. Stop with Enter or Ctrl+C.");
        Console.WriteLine();

        foreach (int addr in valves)
        {
            client.ValveCommand(addr, "p:01060201010003");   // W1, see valve-commands.md
            client.ValveCommand(addr, "p:01060201020002");
        }

        var total = Stopwatch.StartNew();
        var sinceStatus = Stopwatch.StartNew();
        long round = 0;
        while (!stop && (duration == null || total.Elapsed < duration))
        {
            round++;
            foreach (int addr in valves)
            {
                foreach (var p in Parameters.All)
                    Single(addr, p);
                if (round % TreeEvery == 1)
                    Tree(addr);
            }

            if (keys && Console.KeyAvailable && Console.ReadKey(intercept: true).Key == ConsoleKey.Enter)
                stop = true;
            if (sinceStatus.Elapsed >= StatusEvery)
            {
                PrintStatus(total.Elapsed, round);
                sinceStatus.Restart();
            }
        }

        Console.WriteLine();
        Console.WriteLine("Result");
        PrintStatus(total.Elapsed, round);
        PrintSummary();
        return errors.Count == 0 && mismatches == 0 ? 0 : 2;
    }

    private void Single(int addr, Parameter p)
    {
        var sw = Stopwatch.StartNew();
        requests++;
        try
        {
            string reply = client.ValveCommand(addr, "p:0B" + p.Id);
            AddLatency(sw.Elapsed.TotalMilliseconds);
            if (!reply.StartsWith("p:00"))
            {
                Count(reply.StartsWith("p:") && reply.Length >= 4 ? $"valve error {reply[2..4]}" : "unexpected reply");
                return;
            }
            ok++;
            if (p.Static)
                Compare($"v{addr} {p.Name}", Parameters.Decode(p, reply));
        }
        catch (Exception e)
        {
            Fail(e);
        }
    }

    private void Tree(int addr)
    {
        var sw = Stopwatch.StartNew();
        requests++;
        try
        {
            var (content, parts) = client.ValveMultiPart(addr, "g:1E18");
            treeMsTotal += sw.Elapsed.TotalMilliseconds;
            trees++;
            treeParts += parts;
            ok++;
            string hash = Convert.ToHexString(SHA256.HashData(Encoding.ASCII.GetBytes(content)))[..12];
            Compare($"v{addr} tree", $"{content.Length} chars, {parts} parts, sha256 {hash}");
        }
        catch (Exception e)
        {
            Fail(e);
        }
    }

    private void Compare(string key, string value)
    {
        if (!reference.TryGetValue(key, out var first))
        {
            reference[key] = value;
            return;
        }
        if (first != value)
        {
            mismatches++;
            Console.WriteLine($"  MISMATCH {key}: \"{first}\" -> \"{value}\"");
        }
    }

    private void Fail(Exception e)
    {
        string kind = e switch
        {
            BridgeErrorException b => "bridge: " + b.Reason.Split(' ')[0],   // timeout, busy, send, ...
            TimeoutException => "PC timeout (no reply line)",
            _ => "other: " + e.GetType().Name,
        };
        Count(kind);
        Console.WriteLine($"  {DateTime.Now:HH:mm:ss} {e.Message}");
        client.Drain(TimeSpan.FromMilliseconds(500));        // drop a late reply so it cannot match the next request
    }

    private void Count(string kind) => errors[kind] = errors.GetValueOrDefault(kind) + 1;

    private void PrintStatus(TimeSpan elapsed, long round)
    {
        long errorCount = errors.Values.Sum();
        double rate = requests / Math.Max(0.001, elapsed.TotalSeconds);
        string lat = latencyCount == 0 ? "-" :
            $"avg {latencySum / latencyCount:0.0} / p99 {Percentile(0.99):0.0} / max {latencyMax:0.0} ms";
        Console.WriteLine($"  {elapsed:hh\\:mm\\:ss}  round {round,6}  requests {requests,8} ({rate,5:0} /s)  " +
                          $"errors {errorCount}  mismatches {mismatches}  trees {trees}  latency {lat}");
    }

    private void PrintSummary()
    {
        Console.WriteLine();
        Console.WriteLine($"  OK                {ok} of {requests}");
        foreach (var (kind, count) in errors.OrderByDescending(e => e.Value))
            Console.WriteLine($"  {kind,-30} {count}");
        Console.WriteLine($"  Mismatches        {mismatches}");
        if (trees > 0)
            Console.WriteLine($"  Tree reads        {trees}, avg {treeParts / (double)trees:0} parts, avg {treeMsTotal / trees:0} ms");
        foreach (var (key, value) in reference.OrderBy(r => r.Key))
            Console.WriteLine($"  {key,-28} {value}");
        Console.WriteLine();
        Console.WriteLine(errors.Count == 0 && mismatches == 0 ? "  PASSED" : "  FAILED");
    }

    private void AddLatency(double ms)
    {
        histogram[(int)Math.Min(histogram.Length - 1, ms * 10)]++;
        latencyCount++;
        latencySum += ms;
        latencyMax = Math.Max(latencyMax, ms);
    }

    private double Percentile(double q)
    {
        long target = (long)Math.Ceiling(q * latencyCount), seen = 0;
        for (int i = 0; i < histogram.Length; i++)
        {
            seen += histogram[i];
            if (seen >= target)
                return (i + 1) / 10.0;          // upper edge of the bucket
        }
        return latencyMax;
    }
}
