// SyncVerseRGB/Devices/MsiM99ProDevice.cs
using SyncVerseRGB.Core;
using SyncVerseRGB.Drivers;
using System;
using System.Drawing;
using System.Threading;
using System.Threading.Tasks;

namespace SyncVerseRGB.Devices
{
    public sealed class MsiM99ProDevice : ILightController
    {
        private readonly string _dllPath;
        private readonly MsiM99DriverWrapper _drv = new();
        private bool _initialized;

        public MsiM99ProDevice(string dllPath)
        {
            _dllPath = dllPath ?? throw new ArgumentNullException(nameof(dllPath));
        }

        public string Name => "MSI M99 Pro RGB Mouse (Vendor DLL)";
        public bool IsConnected => _initialized;


        public async Task InitializeAsync(CancellationToken ct = default)
        {
            await Task.Yield();

            try
            {
                Console.WriteLine($"[M99Device] Attempting to load MSI driver from: {_dllPath}");
                _drv.Load(_dllPath);

                bool ok1 = _drv.SetVidPid(0x0DB0, 0x8888);
                Console.WriteLine($"[M99Device] Set_VIDPID returned: {ok1}");

                bool ok2 = _drv.OpenReport();
                Console.WriteLine($"[M99Device] Open_ReportDevice returned: {ok2}");

                _initialized = true;
                Console.WriteLine($"[M99Device] Driver loaded OK: {_drv.LoadedPath}");
            }
            catch (Exception ex)
            {
                _initialized = false;
                Console.WriteLine($"[M99Device] Initialization failed: {ex.Message}");
                throw;
            }
        }


        public async Task<bool> ProbeAsync(CancellationToken ct = default)
        {
            await Task.Yield();
            return true;
        }


        // Main static RGB setter using WriteUSB only
        public async Task SetStaticAsync(Color color, CancellationToken ct = default)
        {
            await Task.Yield();
            if (!_initialized)
                await InitializeAsync(ct);

            // Base 59 bytes
            byte[] packet59 =
            {
                0x1B,0x00,0xA0,0x89,0xEC,0x53,0x8F,0x88,0xFF,0xFF,0x00,0x00,0x00,0x00,0x09,0x00,
                0x00,0x01,0x00,0x05,0x00,0x03,0x01,0x20,0x00,0x00,0x00,

                // RGB
                color.R, color.G, color.B,

                0x00,0xFF,0x00,0x00,0x00,0xFF,0xFF,0x00,0x00,0xFF,0xFF,
                0xFF,0x00,0xFF,0xFF,0xFF,0x80,0x00,0xFF,0xFF,0xFF,0x00,
                0x00,0x00,0x00,0x00,0x00,0x00,0x00
            };

            // Always pad to full 64 bytes
            byte[] buffer = new byte[64];
            Array.Copy(packet59, buffer, packet59.Length);

            Console.WriteLine("[M99Device] RawWrite => " + RawWrite(buffer));
        }


        // RawWrite path with safety guards
        public bool RawWrite(byte[] buffer)
        {
            if (!_initialized)
            {
                Console.WriteLine("[M99Device] RawWrite ignored (device not initialized)");
                return false;
            }

            if (buffer == null)
            {
                Console.WriteLine("[M99Device] RawWrite null buffer");
                return false;
            }

            if (buffer.Length != 64)
            {
                Console.WriteLine("[M99Device] RawWrite wrong size: " + buffer.Length);
                return false; // prevent native crash
            }

            return _drv.WriteUSB(buffer);
        }


        public async Task SetBytesAsync(ReadOnlyMemory<byte> data, CancellationToken ct = default)
        {
            // Do nothing — feature reports not supported on this device
            await Task.Yield();
        }


        public async ValueTask DisposeAsync()
        {
            await Task.Yield();
            try { _drv.Dispose(); } catch { }
        }
    }
}
