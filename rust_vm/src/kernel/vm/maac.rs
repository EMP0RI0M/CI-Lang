use crate::mm::{Memory, Value};

#[derive(Debug, Clone)]
pub struct MaacController {
    pub tau_threshold: f64,
    pub cooling_rate: f64,
    pub divergence_metric: f64,
}

impl MaacController {
    pub fn new(tau: f64, cooling: f64) -> Self {
        Self {
            tau_threshold: tau,
            cooling_rate: cooling,
            divergence_metric: 0.0,
        }
    }

    /// Evaluates the variance of active memory cells.
    /// This acts as a proxy for the system's Shannon Entropy or divergence metric $D(t)$.
    pub fn evaluate_entropy(&mut self, memory: &Memory) -> f64 {
        let mut sum = 0.0;
        let mut count = 0;
        
        // Measure volatility in variables
        for cell in memory.values() {
            if let Value::Float(f) = cell.value {
                // A simplified variance/entropy metric
                sum += f.abs(); 
                count += 1;
            }
        }
        
        if count > 0 {
            // Combine current state with historical divergence using an exponential moving average
            let current_variance = sum / (count as f64);
            self.divergence_metric = (self.divergence_metric * 0.8) + (current_variance * 0.2);
        }
        
        self.divergence_metric
    }
    
    pub fn is_diverging(&self) -> bool {
        self.divergence_metric > self.tau_threshold
    }
    
    pub fn get_divergence(&self) -> f64 {
        self.divergence_metric
    }
    
    pub fn cool_down(&mut self) {
        self.divergence_metric *= 1.0 - self.cooling_rate;
    }
}
