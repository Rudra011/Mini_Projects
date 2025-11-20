// SyncVerseRGB/Services/HidEnumerator.cs
namespace SyncVerseRGB.Services;

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;

public sealed record HidDeviceInfo(
    string DevicePath,
    int Vid,
    int Pid,
    ushort UsagePage,
    ushort Usage,
    short FeatureReportByteLength);

public sealed class HidEnumerator
{
    public IEnumerable<HidDeviceInfo> Enumerate()
    {
        HidNative.HidD_GetHidGuid(out var hidGuid);

        IntPtr devs = HidNative.SetupDiGetClassDevs(ref hidGuid, null, IntPtr.Zero,
            HidNative.DIGCF_PRESENT | HidNative.DIGCF_DEVICEINTERFACE);

        if (devs == IntPtr.Zero)
        {
            Console.WriteLine("[HID] SetupDiGetClassDevs returned null.");
            yield break;
        }

        try
        {
            uint index = 0;
            var ifaceData = new HidNative.SP_DEVICE_INTERFACE_DATA
            {
                cbSize = (uint)Marshal.SizeOf<HidNative.SP_DEVICE_INTERFACE_DATA>()
            };

            while (HidNative.SetupDiEnumDeviceInterfaces(devs, IntPtr.Zero, ref hidGuid, index, ref ifaceData))
            {
                index++;

                // First call to get required size (ERROR_INSUFFICIENT_BUFFER expected)
                HidNative.SetupDiGetDeviceInterfaceDetail(devs, ref ifaceData, IntPtr.Zero, 0, out int required, IntPtr.Zero);
                if (required <= 0)
                {
                    Console.WriteLine("[HID] Unexpected required size 0 when querying interface detail.");
                    continue;
                }

                // Allocate unmanaged buffer for SP_DEVICE_INTERFACE_DETAIL_DATA (variable-length struct)
                IntPtr detailBuffer = Marshal.AllocHGlobal(required);
                try
                {
                    // For Unicode, cbSize must be sizeof(uint) + sizeof(char) on x86 (6) and 8 on x64
                    int cb = (IntPtr.Size == 8) ? 8 : 6;
                    Marshal.WriteInt32(detailBuffer, cb);

                    if (!HidNative.SetupDiGetDeviceInterfaceDetail(devs, ref ifaceData, detailBuffer, required, out _, IntPtr.Zero))
                    {
                        int err = Marshal.GetLastWin32Error();
                        Console.WriteLine($"[HID] SetupDiGetDeviceInterfaceDetail failed: {err}");
                        continue;
                    }

                    // Read DevicePath from buffer at offset cb
                    string path = Marshal.PtrToStringAuto(detailBuffer + cb) ?? string.Empty;

                    int vid = TryParseHex(path, "vid_");
                    int pid = TryParseHex(path, "pid_");

                    short featureLen = 0;
                    ushort usagePage = 0, usage = 0;

                    using var handle = OpenForCaps(path);
                    if (!handle.IsInvalid && !handle.IsClosed)
                    {
                        if (HidNative.HidD_GetPreparsedData(handle, out var prep))
                        {
                            try
                            {
                                int nt = HidNative.HidP_GetCaps(prep, out var caps);
                                if (nt == 0)
                                {
                                    featureLen = caps.FeatureReportByteLength;
                                    usagePage = (ushort)caps.UsagePage;
                                    usage = (ushort)caps.Usage;
                                }
                                else
                                {
                                    Console.WriteLine($"[HID] HidP_GetCaps NTSTATUS=0x{nt:X8}");
                                }
                            }
                            finally
                            {
                                HidNative.HidD_FreePreparsedData(prep);
                            }
                        }
                        else
                        {
                            Console.WriteLine($"[HID] HidD_GetPreparsedData failed: {Marshal.GetLastWin32Error()}");
                        }
                    }

                    Console.WriteLine($"[HID] {path}");
                    Console.WriteLine($"      VID=0x{vid:X4} PID=0x{pid:X4} UsagePage=0x{usagePage:X4} Usage=0x{usage:X4} FeatureLen={featureLen}");

                    yield return new HidDeviceInfo(path, vid, pid, usagePage, usage, featureLen);
                }
                finally
                {
                    Marshal.FreeHGlobal(detailBuffer);
                }
            }
        }
        finally
        {
            HidNative.SetupDiDestroyDeviceInfoList(devs);
        }
    }

    private static int TryParseHex(string path, string key)
    {
        var idx = path.IndexOf(key, StringComparison.OrdinalIgnoreCase);
        if (idx < 0) return 0;
        idx += key.Length;
        var span = path.AsSpan(idx);
        if (span.Length < 4) return 0;
        var hex = span.Slice(0, 4).ToString();
        return int.TryParse(hex, NumberStyles.HexNumber, CultureInfo.InvariantCulture, out int val) ? val : 0;
    }

    private static SafeFileHandle OpenForCaps(string devicePath)
    {
        var handle = HidNative.CreateFile(
            devicePath,
            HidNative.GENERIC_READ,
            HidNative.FILE_SHARE_READ | HidNative.FILE_SHARE_WRITE,
            IntPtr.Zero,
            HidNative.OPEN_EXISTING,
            0,
            IntPtr.Zero);

        if (handle.IsInvalid)
            Console.WriteLine($"[HID] OpenForCaps failed: {Marshal.GetLastWin32Error()}");

        return handle;
    }

    public static void SetFeature(SafeFileHandle handle, byte[] buffer)
    {
        if (!HidNative.HidD_SetFeature(handle, buffer, buffer.Length))
        {
            int err = Marshal.GetLastWin32Error();
            throw new IOException($"HidD_SetFeature failed: {err}");
        }
    }
}
