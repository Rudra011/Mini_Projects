// SyncVerseRGB/Core/DeviceManager.cs
namespace SyncVerseRGB.Core;

using SyncVerseRGB.Devices;
using SyncVerseRGB.Services;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

public sealed class DeviceManager : IAsyncDisposable
{
    public List<ILightController> Controllers { get; } = new();

    // Explicit MSI driver path — your installed location
    private const string ExplicitMsiDriverPath = 
        @"D:\Softwares\MSI GAMING MOUSE M99 Pro\MSDriver.dll";

    public async Task DetectAsync(CancellationToken ct = default)
    {
        Controllers.Clear();

        var hid = new HidEnumerator();
        var all = hid.Enumerate().ToList();

        // ----- Firefly -----
        var fireflyInfo = PreferVendorUsage(all.Where(d => d.Vid == 0x04D9 && d.Pid == 0xA1CD));
        if (fireflyInfo != null)
        {
            var firefly = new FireflyDevice(fireflyInfo.DevicePath);
            if (await firefly.ProbeAsync(ct))
                Controllers.Add(firefly);
        }

        // ----- MSI M99 Pro -----
        var m99Info = PreferVendorUsage(all.Where(d => d.Vid == 0x04D9 && d.Pid == 0xA31C));

        if (m99Info != null)
        {
            Console.WriteLine("[DeviceManager] M99 HID present. Using vendor DLL approach.");
            Controllers.Add(new MsiM99ProDevice(ExplicitMsiDriverPath));
        }
        else
        {
            // Fallback: use explicit path directly
            if (File.Exists(ExplicitMsiDriverPath))
            {
                Console.WriteLine($"[DeviceManager] Using explicit M99 DLL: {ExplicitMsiDriverPath}");
                Controllers.Add(new MsiM99ProDevice(ExplicitMsiDriverPath));
            }
            else if (TryFindMsDriverPath(out var msPath))
            {
                Console.WriteLine($"[DeviceManager] Auto-discovered MSDriver.dll at: {msPath}");
                Controllers.Add(new MsiM99ProDevice(msPath));
            }
            else
            {
                Console.WriteLine("[DeviceManager] MSDriver.dll not found; MSI M99 device not added.");
            }
        }

        // ----- SteelSeries GameSense -----
        var steel = new SteelSeriesGameSenseDevice();
        if (await steel.ProbeAsync(ct))
            Controllers.Add(steel);

        // ----- Initialize all Controllers -----
        foreach (var c in Controllers.ToArray())
        {
            try
            {
                await c.InitializeAsync(ct);
                Console.WriteLine($"[DeviceManager] Initialized: {c.Name}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[DeviceManager] Init failed for {c.Name}: {ex.Message}");
            }
        }
    }

    private static HidDeviceInfo? PreferVendorUsage(IEnumerable<HidDeviceInfo> list)
        => list.OrderByDescending(d => d.UsagePage >= 0xFF00).ThenBy(d => d.DevicePath).FirstOrDefault();

    private static bool TryFindMsDriverPath(out string path)
    {
        var candidates = new[]
        {
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "MSI", "MSDriver.dll"),
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "MSI", "MSDriver.dll"),
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "MSI", "MSDriver", "MSDriver.dll"),
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "MSI", "MSDriver", "MSDriver.dll"),
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "MSI Center", "MSDriver.dll"),
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "MSI Center", "MSDriver.dll"),
            Path.Combine(AppContext.BaseDirectory, "MSDriver.dll"),
        };

        foreach (var c in candidates)
        {
            if (File.Exists(c))
            {
                path = c;
                return true;
            }
        }

        path = string.Empty;
        return false;
    }

    public async ValueTask DisposeAsync()
    {
        foreach (var c in Controllers)
        {
            try
            {
                await c.DisposeAsync();
            }
            catch
            {
                // ignore
            }
        }

        Controllers.Clear();
    }
}
