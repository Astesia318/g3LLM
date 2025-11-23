xtuner train xtuner/llama3_8b_instruct_qlora_alpaca_e3_M.py
xtuner convert pth_to_hf xtuner/llama3_8b_instruct_qlora_alpaca_e3_M.py ./work_dirs/llama3_8b_instruct_qlora_alpaca_e3_M/epoch_3.pth ./hf_llama3
xtuner convert merge /root/zzgroup3/xtuner_finetune/model_cache/Llama/Meta-Llama-3-8B-Instruct ./hf_llama3 ./merged_Llama3_8b_instruct --max-shard-size 2GB