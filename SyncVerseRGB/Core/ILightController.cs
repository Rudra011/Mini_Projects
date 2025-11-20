namespace SyncVerseRGB.Core;

using System.Drawing;

public interface ILightController : IAsyncDisposable
{
    string Name { get; }
    bool IsConnected { get; }

    Task InitializeAsync(CancellationToken ct = default);
    Task<bool> ProbeAsync(CancellationToken ct = default); // detect/confirm device presence

    Task SetStaticAsync(Color color, CancellationToken ct = default);

    // Future: animations/effects can plug into this
    Task SetBytesAsync(ReadOnlyMemory<byte> featureReport, CancellationToken ct = default);
}
