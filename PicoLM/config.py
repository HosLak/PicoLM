from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ModelConfig:
    # Model architecture
    d_model: int = 256
    n_heads: int = 8
    n_kv_heads: int = field(init=False)
    n_layers: int = 8
    
    d_ff: int = field(init=False)
    batch_size: int = 16
    max_steps: int = 1500 # max_tokens // (batch_size * gradient_accumulation_steps * max_seq_len) = 1 epoch
    rope_theta: float = 10000.0

    # Training parameters
    gradient_accumulation_steps: int = 4 # 16 * 4 = 64
    muon_lr: float = 0.01

    # Data parameters
    max_seq_len: int = 256
    multiple_of: int = 128
    stride: int = field(init=False)
    max_tokens: int = 21413859 # 21,413,859 if you want to ues entire of dataset

    # Evaluation
    eval_every: int = 150
    eval_steps: int = 30

    # Regularization
    weight_decay: float = 0.1
    dropout: float = 0.0
    grad_clip: float = 1.0

    # Technical
    use_amp: bool = True
    vocab_size: Optional[int] = None

    def __post_init__(self):
        self.d_k = self.d_model // self.n_heads
        assert self.d_model % self.n_heads == 0, "d_model must be divisible by n_heads"
        
        # Set stride conditionally
        if self.max_tokens > 10000000:
            self.stride = self.max_seq_len // 2
        else:
            self.stride = self.max_seq_len
        
        # Set d_ff to 4 times d_model
        self.d_ff = int(self.multiple_of * int((((self.d_model * 4 * 2 / 3) * 1.3) + self.multiple_of + 1) // self.multiple_of))
        
        self.n_kv_heads = self.n_heads // 4
