namespace SyncVerseRGB.Services;

using System.Drawing;
using System.Drawing.Imaging;
using System.Windows.Forms; // Requires net8.0-windows; implicit ref

public sealed class DisplaySampler
{
    private readonly Bitmap _buffer;

    public DisplaySampler()
    {
        _buffer = new Bitmap(64, 36); // downsample buffer
    }

    public Color SampleAverageColor()
    {
        var bounds = Screen.PrimaryScreen?.Bounds ?? new Rectangle(0, 0, 1920, 1080);
        using var screenBmp = new Bitmap(bounds.Width, bounds.Height);
        using (var g = Graphics.FromImage(screenBmp))
        {
            g.CopyFromScreen(bounds.Location, Point.Empty, bounds.Size);
        }

        // Scale to tiny buffer to approximate average fast
        using (var g2 = Graphics.FromImage(_buffer))
        {
            g2.DrawImage(screenBmp, new Rectangle(0, 0, _buffer.Width, _buffer.Height));
        }

        // Average pixels
        long tr = 0, tg = 0, tb = 0; int count = _buffer.Width * _buffer.Height;
        var data = _buffer.LockBits(new Rectangle(0, 0, _buffer.Width, _buffer.Height), ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
        try
        {
            unsafe
            {
                for (int y = 0; y < _buffer.Height; y++)
                {
                    byte* row = (byte*)data.Scan0 + y * data.Stride;
                    for (int x = 0; x < _buffer.Width; x++)
                    {
                        byte b = row[x * 3 + 0];
                        byte g = row[x * 3 + 1];
                        byte r = row[x * 3 + 2];
                        tr += r; tg += g; tb += b;
                    }
                }
            }
        }
        finally { _buffer.UnlockBits(data); }

        return Color.FromArgb((byte)(tr / count), (byte)(tg / count), (byte)(tb / count));
    }
}
