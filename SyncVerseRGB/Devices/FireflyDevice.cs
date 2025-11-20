// SyncVerseRGB/Devices/FireflyDevice.cs
namespace SyncVerseRGB.Devices;

using Microsoft.Win32.SafeHandles;
using SyncVerseRGB.Core;
using SyncVerseRGB.Services;
using System;
using System.Drawing;
using System.Runtime.InteropServices;

public sealed class FireflyDevice : ILightController
{
    private readonly string _path;
    private SafeFileHandle? _handle;

    private const byte REPORT_ID = 0x08;
    private short _featureLen; // obtained from HID caps

    public FireflyDevice(string devicePath) => _path = devicePath;

    public string Name => "Cosmic Byte Firefly RGB (04D9:A1CD)";
    public bool IsConnected => _handle is { IsInvalid: false } && !_handle.IsClosed;

    public async Task InitializeAsync(CancellationToken ct = default)
    {
        await Task.Yield();
        EnsureHandle();
        EnsureCaps();
    }

    public async Task<bool> ProbeAsync(CancellationToken ct = default)
    {
        await Task.Yield();
        return true; // VID/PID already matched by DeviceManager
    }

    public async Task SetStaticAsync(Color color, CancellationToken ct = default)
    {
        await Task.Yield();
        try
        {
            EnsureHandle();
            EnsureCaps();

            var len = _featureLen > 0 ? _featureLen : (short)65;
            var buf = new byte[len];

            buf[0] = REPORT_ID; // feature report id at index 0
            buf[1] = 0x01;      // mode: static (empirical)
            buf[2] = 0x64;      // brightness 0..100
            buf[3] = 0x00;      // speed (unused here)
            buf[4] = 0x00;      // direction (unused)
            buf[5] = color.R;   // R
            buf[6] = color.G;   // G
            buf[7] = color.B;   // B

            HidEnumerator.SetFeature(_handle!, buf);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Firefly] SetStatic failed: {ex.Message}");
            ReopenOnFailure();
        }
    }

    public async Task SetBytesAsync(ReadOnlyMemory<byte> featureReport, CancellationToken ct = default)
    {
        await Task.Yield();
        try
        {
            EnsureHandle();
            EnsureCaps();

            var src = featureReport.ToArray();
            if (src.Length == 0 || src[0] != REPORT_ID)
                throw new ArgumentException("Firefly feature report must begin with Report ID 0x08.");

            var len = _featureLen > 0 ? _featureLen : (short)65;
            var buf = new byte[len];
            Array.Copy(src, 0, buf, 0, Math.Min(src.Length, buf.Length));

            HidEnumerator.SetFeature(_handle!, buf);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Firefly] SetBytes failed: {ex.Message}");
            ReopenOnFailure();
        }
    }

    private void EnsureCaps()
    {
        if (_handle == null || _handle.IsInvalid || _handle.IsClosed) return;
        if (_featureLen > 0) return;

        if (!HidNative.HidD_GetPreparsedData(_handle, out var prep))
        {
            Console.WriteLine($"[Firefly] GetPreparsedData failed: {Marshal.GetLastWin32Error()}");
            _featureLen = 65;
            return;
        }

        try
        {
            int nt = HidNative.HidP_GetCaps(prep, out var caps);
            if (nt == 0)
            {
                _featureLen = caps.FeatureReportByteLength > 0 ? caps.FeatureReportByteLength : (short)65;
                Console.WriteLine($"[Firefly] FeatureReportLen={_featureLen} (UsagePage=0x{caps.UsagePage:X4}, Usage=0x{caps.Usage:X4})");
            }
            else
            {
                Console.WriteLine($"[Firefly] HidP_GetCaps NTSTATUS={nt:X8}");
                _featureLen = 65;
            }
        }
        finally
        {
            HidNative.HidD_FreePreparsedData(prep);
        }
    }

    private void EnsureHandle()
    {
        if (_handle == null || _handle.IsInvalid || _handle.IsClosed)
            _handle = OpenWriteOnlyWithRetry(_path);
    }

    private static SafeFileHandle OpenWriteOnlyWithRetry(string devicePath)
    {
        // First: strict (no share)
        var h = HidNative.CreateFile(
            devicePath,
            HidNative.GENERIC_WRITE,
            0,
            IntPtr.Zero,
            HidNative.OPEN_EXISTING,
            0,
            IntPtr.Zero);

        if (h.IsInvalid)
        {
            int err = Marshal.GetLastWin32Error();
            Console.WriteLine($"[Firefly] Open WRITE no-share failed: {err}. Retrying with share…");

            // Retry: allow sharing if vendor tool holds a handle
            h = HidNative.CreateFile(
                devicePath,
                HidNative.GENERIC_WRITE,
                HidNative.FILE_SHARE_READ | HidNative.FILE_SHARE_WRITE,
                IntPtr.Zero,
                HidNative.OPEN_EXISTING,
                0,
                IntPtr.Zero);

            if (h.IsInvalid)
            {
                err = Marshal.GetLastWin32Error();
                throw new IOException($"[Firefly] Open failed: {err}");
            }
        }

        return h;
    }

    private void ReopenOnFailure()
    {
        try
        {
            _handle?.Dispose();
            _handle = OpenWriteOnlyWithRetry(_path);
            _featureLen = 0; // requery caps
        }
        catch { /* keep engine alive */ }
    }

    public async ValueTask DisposeAsync()
    {
        await Task.Yield();
        _handle?.Dispose();
        _handle = null;
        _featureLen = 0;
    }
}
