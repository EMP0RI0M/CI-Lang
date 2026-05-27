use bootloader_api::info::{FrameBufferInfo, PixelFormat};
use spin::Mutex;

pub static WRITER: Mutex<Option<Writer>> = Mutex::new(None);

pub struct Writer {
    buffer: &'static mut [u8],
    info: FrameBufferInfo,
    x_pos: usize,
    y_pos: usize,
}

impl Writer {
    pub fn new(buffer: &'static mut [u8], info: FrameBufferInfo) -> Self {
        Self { buffer, info, x_pos: 0, y_pos: 0 }
    }

    pub fn write_byte(&mut self, byte: u8) {
        match byte {
            b'\n' => self.newline(),
            _ => {
                self.x_pos += 8;
                if self.x_pos >= self.info.width { self.newline(); }
            }
        }
    }

    fn newline(&mut self) {
        self.y_pos += 16;
        self.x_pos = 0;
    }
}

pub fn init(buffer: &'static mut [u8], info: FrameBufferInfo) {
    *WRITER.lock() = Some(Writer::new(buffer, info));
}

#[macro_export]
macro_rules! kernel_print {
    ($($arg:tt)*) => ($crate::drivers::display::_print(format_args!($($arg)*)));
}

#[macro_export]
macro_rules! kernel_println {
    () => ($crate::kernel_print!("\n"));
    ($($arg:tt)*) => ($crate::kernel_print!("{}\n", format_args!($($arg)*)));
}

#[doc(hidden)]
pub fn _print(args: core::fmt::Arguments) {
    use core::fmt::Write;
    struct WriteWrapper;
    impl core::fmt::Write for WriteWrapper {
        fn write_str(&mut self, s: &str) -> core::fmt::Result {
            let mut writer = WRITER.lock();
            if let Some(w) = writer.as_mut() {
                for byte in s.bytes() { w.write_byte(byte); }
            }
            Ok(())
        }
    }
    let _ = WriteWrapper.write_fmt(args);
}
