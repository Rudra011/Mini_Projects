// SyncVerseRGB/Devices/SteelSeriesGameSenseDevice.cs
namespace SyncVerseRGB.Devices;

using SyncVerseRGB.Core;
using System;
using System.Drawing;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;

public sealed class SteelSeriesGameSenseDevice : ILightController
{
    private HttpClient? _http;
    private string? _baseUrl; // e.g., http://127.0.0.1:51xxx
    private const string GAME = "SYNCVERSE";

    public string Name => "SteelSeries GameSense (MSI Laptop Keyboard)";
    public bool IsConnected => _http != null && _baseUrl != null;

    public async Task InitializeAsync(CancellationToken ct = default)
    {
        await Task.Yield();

        _http ??= new HttpClient();
        _baseUrl ??= TryReadCoreProps();

        Console.WriteLine($"[GameSense] baseUrl = {_baseUrl}");

        if (_baseUrl == null)
            throw new InvalidOperationException("SteelSeries coreProps not found; is SteelSeries GG running?");

        // Reset registration
        try
        {
            var respDel = await _http.PostAsJsonAsync($"{_baseUrl}/remove_game", new { game = GAME }, ct);
            var cDel = await respDel.Content.ReadAsStringAsync(ct);
            Console.WriteLine($"[GameSense] remove_game {(int)respDel.StatusCode} {cDel}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[GameSense] remove_game exception: {ex.Message}");
        }

        var meta = new
        {
            game = GAME,
            game_display_name = "SyncVerse RGB",
            developer = "SyncVerse"
        };
        var respMeta = await _http.PostAsJsonAsync($"{_baseUrl}/game_metadata", meta, ct);
        var cMeta = await respMeta.Content.ReadAsStringAsync(ct);
        Console.WriteLine($"[GameSense] game_metadata {(int)respMeta.StatusCode} {cMeta}");
        respMeta.EnsureSuccessStatusCode();

        var bind = new
        {
            game = GAME,
            @event = "COLOR",
            min_value = 0,
            max_value = 100,
            handlers = new[]
            {
                new
                {
                    device_type = "keyboard",
                    zone = "all",
                    mode = "color",
                    color = new { red = 0, green = 0, blue = 0 }
                }
            }
        };
        var respBind = await _http.PostAsJsonAsync($"{_baseUrl}/bind_event", bind, ct);
        var cBind = await respBind.Content.ReadAsStringAsync(ct);
        Console.WriteLine($"[GameSense] bind_event {(int)respBind.StatusCode} {cBind}");
        respBind.EnsureSuccessStatusCode();
    }

    public async Task<bool> ProbeAsync(CancellationToken ct = default)
    {
        await Task.Yield();
        return TryReadCoreProps() != null;
    }

    public async Task SetStaticAsync(Color color, CancellationToken ct = default)
    {
        if (_http == null || _baseUrl == null)
            await InitializeAsync(ct);

        // Primary: frame schema
        var payloadA = new
        {
            game = GAME,
            @event = "COLOR",
            data = new
            {
                frame = new
                {
                    r = (int)color.R,
                    g = (int)color.G,
                    b = (int)color.B
                }
            }
        };
        var respA = await _http!.PostAsJsonAsync($"{_baseUrl}/game_event", payloadA, ct);
        var cA = await respA.Content.ReadAsStringAsync(ct);
        Console.WriteLine($"[GameSense] game_event/frame {(int)respA.StatusCode} {cA}");

        if (!respA.IsSuccessStatusCode)
        {
            // Fallback: color schema
            var payloadB = new
            {
                game = GAME,
                @event = "COLOR",
                data = new
                {
                    color = new
                    {
                        red = (int)color.R,
                        green = (int)color.G,
                        blue = (int)color.B
                    }
                }
            };
            var respB = await _http.PostAsJsonAsync($"{_baseUrl}/game_event", payloadB, ct);
            var cB = await respB.Content.ReadAsStringAsync(ct);
            Console.WriteLine($"[GameSense] game_event/color {(int)respB.StatusCode} {cB}");
            respB.EnsureSuccessStatusCode();
        }
        else
        {
            respA.EnsureSuccessStatusCode();
        }
    }

    public async Task SetBytesAsync(ReadOnlyMemory<byte> featureReport, CancellationToken ct = default)
    {
        // Interpret first 3 bytes as RGB; copy to heap to avoid Span across await
        var mem = featureReport.ToArray();
        if (mem.Length < 3) return;

        await SetStaticAsync(Color.FromArgb(mem[0], mem[1], mem[2]), ct);
    }

    public async ValueTask DisposeAsync()
    {
        if (_http != null && _baseUrl != null)
        {
            try
            {
                var resp = await _http.PostAsJsonAsync($"{_baseUrl}/remove_game", new { game = GAME });
                var c = await resp.Content.ReadAsStringAsync();
                Console.WriteLine($"[GameSense] remove_game {(int)resp.StatusCode} {c}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[GameSense] remove_game exception on dispose: {ex.Message}");
            }
        }

        _http?.Dispose();
        _http = null;
        _baseUrl = null;

        await Task.CompletedTask;
    }

    private static string? TryReadCoreProps()
{
    var dirs = new[]
    {
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "SteelSeries", "SteelSeries GG", "coreProps.json"),
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "SteelSeries", "SteelSeries Engine 3", "coreProps.json"),
    };

    // DEBUG: Print all paths being checked
    Console.WriteLine("=== GameSense coreProps.json search paths ===");
    foreach (var p in dirs)
    {
        try
        {
            Console.WriteLine($"  {p}   exists={File.Exists(p)}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"  {p}   exception: {ex.Message}");
        }
    }

    foreach (var file in dirs)
    {
        if (File.Exists(file))
        {
            try
            {
                Console.WriteLine($"=== Reading coreProps.json from: {file} ===");

                var json = JsonDocument.Parse(File.ReadAllText(file));
                if (json.RootElement.TryGetProperty("address", out var addr))
                {
                    var a = addr.GetString();
                    Console.WriteLine($"=== Loaded SteelSeries address from JSON: {a} ===");

                    if (!string.IsNullOrWhiteSpace(a))
                        return $"http://{a}";
                }
                else
                {
                    Console.WriteLine($"!!! 'address' property not found in {file}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"!!! Error reading {file}: {ex.Message}");
            }
        }
    }

    Console.WriteLine("!!! No valid coreProps.json found.");
    return null;
}

}
