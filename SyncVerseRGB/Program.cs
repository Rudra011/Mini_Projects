// SyncVerseRGB/Program.cs
using System;
using System.Linq;
using System.Drawing;
using System.Threading.Tasks;
using SyncVerseRGB.Core;
using SyncVerseRGB.Devices;
using SyncVerseRGB.Services;

namespace SyncVerseRGB
{
    internal static class Program
    {
        private static async Task Main(string[] args)
        {
            Console.WriteLine("SyncVerse RGB — console prototype\n");

            var mgr = new DeviceManager();
            await mgr.DetectAsync();

            Console.WriteLine("Devices detected:");
            foreach (var dev in mgr.Controllers)
                Console.WriteLine($" - {dev.Name}");
            Console.WriteLine();

            Console.WriteLine("Commands: static R G B | off | raw ... | exit");

            while (true)
            {
                Console.Write("> ");
                var line = Console.ReadLine();
                if (line == null) continue;

                var parts = line.Trim().Split(' ', StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length == 0) continue;

                switch (parts[0].ToLower())
                {
                    case "exit":
                        try { await mgr.DisposeAsync(); } catch { }
                        return;

                    case "off":
                        foreach (var d in mgr.Controllers)
                            await d.SetStaticAsync(Color.Black);
                        Console.WriteLine("Off");
                        break;

                    case "static":
                        if (parts.Length == 4 &&
                            int.TryParse(parts[1], out int r) &&
                            int.TryParse(parts[2], out int g) &&
                            int.TryParse(parts[3], out int b))
                        {
                            var c = Color.FromArgb(r, g, b);
                            foreach (var dev in mgr.Controllers)
                                await dev.SetStaticAsync(c);

                            Console.WriteLine($"Static color set: R{r} G{g} B{b}");
                        }
                        else
                        {
                            Console.WriteLine("Usage: static R G B");
                        }
                        break;

                    case "raw":
                        if (parts.Length < 2)
                        {
                            Console.WriteLine("Usage: raw HEX HEX HEX ...");
                            break;
                        }

                        try
                        {
                            byte[] bytes = parts.Skip(1)
                                .Select(h => Convert.ToByte(h, 16))
                                .ToArray();

                            Console.WriteLine("[RAW] Parsed: " + BitConverter.ToString(bytes));

                            foreach (var dev in mgr.Controllers)
                                if (dev is MsiM99ProDevice m99)
                                    Console.WriteLine("[RAW] => " +
                                        m99.RawWrite(bytes.Length == 64 ? bytes : Pad(bytes)));
                        }
                        catch
                        {
                            Console.WriteLine("Invalid hex format.");
                        }

                        break;

                    default:
                        Console.WriteLine("Unknown command.");
                        break;
                }
            }
        }

        private static byte[] Pad(byte[] src)
        {
            byte[] dst = new byte[64];
            Array.Copy(src, dst, Math.Min(src.Length, 64));
            return dst;
        }
    }
}
