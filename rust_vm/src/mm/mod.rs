pub mod allocator;
pub mod paging;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Value {
    Float(f64),
    Bool(bool),
}

pub struct MemoryCell {
    pub value: Value,
    pub volatility: f64,
}

impl MemoryCell {
    pub fn new(value: Value) -> Self {
        Self { value, volatility: 0.0 }
    }
}

pub struct Memory {
    // Array of key-value pairs for no_std MVP without alloc
    variables: [Option<(&'static str, MemoryCell)>; 16],
    stack: [Option<Value>; 100],
    stack_ptr: usize,
}

impl Memory {
    pub fn new() -> Self {
        Self {
            variables: Default::default(),
            stack: [None; 100],
            stack_ptr: 0,
        }
    }

    pub fn push(&mut self, val: Value) -> Result<(), &'static str> {
        if self.stack_ptr >= 100 { return Err("Stack Overflow"); }
        self.stack[self.stack_ptr] = Some(val);
        self.stack_ptr += 1;
        Ok(())
    }

    pub fn pop(&mut self) -> Result<Value, &'static str> {
        if self.stack_ptr == 0 { return Err("Stack Underflow"); }
        self.stack_ptr -= 1;
        let val = self.stack[self.stack_ptr].take().ok_or("Stack element is None")?;
        Ok(val)
    }

    pub fn store(&mut self, name: &'static str, val: Value) {
        for slot in self.variables.iter_mut() {
            if let Some((k, cell)) = slot {
                if *k == name {
                    cell.value = val;
                    return;
                }
            }
        }
        for slot in self.variables.iter_mut() {
            if slot.is_none() {
                *slot = Some((name, MemoryCell::new(val)));
                return;
            }
        }
    }

    pub fn load(&self, name: &str) -> Option<Value> {
        for slot in self.variables.iter() {
            if let Some((k, cell)) = slot {
                if *k == name { return Some(cell.value); }
            }
        }
        None
    }

    pub fn set_volatility(&mut self, name: &str, volatility: f64) {
        for slot in self.variables.iter_mut() {
            if let Some((k, cell)) = slot {
                if *k == name {
                    cell.volatility = volatility;
                    return;
                }
            }
        }
    }

    pub fn values_mut(&mut self) -> impl Iterator<Item = &mut MemoryCell> {
        self.variables.iter_mut().filter_map(|slot| slot.as_mut().map(|(_, cell)| cell))
    }

    pub fn values(&self) -> impl Iterator<Item = &MemoryCell> {
        self.variables.iter().filter_map(|slot| slot.as_ref().map(|(_, cell)| cell))
    }
}
