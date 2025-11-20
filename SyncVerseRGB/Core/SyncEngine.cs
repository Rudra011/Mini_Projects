namespace SyncVerseRGB.Core;

using SyncVerseRGB.Services;
using System.Drawing;

public sealed class SyncEngine
{
    private readonly IReadOnlyList<ILightController> _controllers;
    private readonly DisplaySampler _sampler;
    private CancellationTokenSource? _loopCts;

    public SyncEngine(IReadOnlyList<ILightController> controllers, DisplaySampler sampler)
    {
        _controllers = controllers;
        _sampler = sampler;
    }

    public async Task SetStaticAsync(Color color, CancellationToken ct = default)
    {
        foreach (var c in _controllers)
        {
            try { await c.SetStaticAsync(color, ct); }
            catch (Exception ex) { Console.WriteLine($"[{c.Name}] static failed: {ex.Message}"); }
        }
    }

    public async Task StartDisplaySyncAsync(int targetFps = 30, CancellationToken ct = default)
    {
        await StopAsync();
        _loopCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        var token = _loopCts.Token;
        _ = Task.Run(async () =>
        {
            var frameTime = TimeSpan.FromSeconds(1.0 / Math.Clamp(targetFps, 1, 60));
            while (!token.IsCancellationRequested)
            {
                try
                {
                    var color = _sampler.SampleAverageColor();
                    foreach (var c in _controllers)
                    {
                        try { await c.SetStaticAsync(color, token); }
                        catch (Exception ex) { Console.WriteLine($"[{c.Name}] display-sync failed: {ex.Message}"); }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Display sampling error: {ex.Message}");
                }
                await Task.Delay(frameTime, token);
            }
        }, token);
    }

    public Task StopAsync()
    {
        _loopCts?.Cancel();
        _loopCts?.Dispose();
        _loopCts = null;
        return Task.CompletedTask;
    }
}
