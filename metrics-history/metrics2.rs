# TYPE smrol_finalize_ready_source counter
smrol_finalize_ready_source{src="pending"} 5
smrol_finalize_ready_source{src="pending_txs"} 392

# TYPE smrol_dispatch_total counter
smrol_dispatch_total{stage="median"} 392
smrol_dispatch_total{stage="final_verify"} 392
smrol_dispatch_total{stage="order_finalize"} 392

# HELP smrol_heartbeat Node heartbeat tick
# TYPE smrol_heartbeat counter
smrol_heartbeat{node="0"} 42

# TYPE smrol_verify_result_total counter
smrol_verify_result_total{stage="final_verify",result="ok"} 392

# HELP smrol_threshold_pending_jobs Current number of pending threshold worker jobs
# TYPE smrol_threshold_pending_jobs gauge
smrol_threshold_pending_jobs{pool="seq_offload"} 0
smrol_threshold_pending_jobs{pool="pnfifo"} 0

# TYPE smrol_inflight gauge
smrol_inflight{stage="final_verify"} 0
smrol_inflight{stage="median"} 0
smrol_inflight{stage="final_sign"} 0
smrol_inflight{stage="order_finalize"} 0

# TYPE smrol_network_writer_backlog gauge
smrol_network_writer_backlog{target="2"} 0
smrol_network_writer_backlog{target="3"} 0
smrol_network_writer_backlog{target="1"} 0

# HELP smrol_channel_backlog Pending messages in asynchronous channels
# TYPE smrol_channel_backlog gauge
smrol_channel_backlog{channel="request"} 0
smrol_channel_backlog{channel="final"} 0
smrol_channel_backlog{channel="order_verify"} 0
smrol_channel_backlog{channel="final_sign"} 0
smrol_channel_backlog{channel="median"} 0
smrol_channel_backlog{channel="order_finalize"} 0
smrol_channel_backlog{channel="response"} 0
smrol_channel_backlog{channel="order"} 0
smrol_channel_backlog{channel="median_combine"} 0
smrol_channel_backlog{channel="final_verify"} 0

# HELP smrol_node_up node is up
# TYPE smrol_node_up gauge
smrol_node_up{node="0"} 1

# HELP smrol_threshold_task_exec_ms Execution time of threshold worker tasks (ms)
# TYPE smrol_threshold_task_exec_ms summary
smrol_threshold_task_exec_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0"} 0.111917
smrol_threshold_task_exec_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0.5"} 0.12412079777728018
smrol_threshold_task_exec_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0.9"} 0.5188709867363265
smrol_threshold_task_exec_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0.95"} 1.1161664430610863
smrol_threshold_task_exec_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0.99"} 2.8465279786080298
smrol_threshold_task_exec_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0.999"} 8.687628500503079
smrol_threshold_task_exec_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="1"} 33.167125
smrol_threshold_task_exec_ms_sum{task="verify_seq_order_batch",pool="seq_offload"} 160.504876
smrol_threshold_task_exec_ms_count{task="verify_seq_order_batch",pool="seq_offload"} 392
smrol_threshold_task_exec_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0"} 1.163875
smrol_threshold_task_exec_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0.5"} 2.434399217011985
smrol_threshold_task_exec_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0.9"} 11.460427372490324
smrol_threshold_task_exec_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0.95"} 15.619185590528923
smrol_threshold_task_exec_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0.99"} 32.152815044928346
smrol_threshold_task_exec_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0.999"} 53.000429019893595
smrol_threshold_task_exec_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="1"} 69.463542
smrol_threshold_task_exec_ms_sum{task="pnfifo_verify_share",pool="pnfifo"} 7579.277172999998
smrol_threshold_task_exec_ms_count{task="pnfifo_verify_share",pool="pnfifo"} 1568
smrol_threshold_task_exec_ms{task="pnfifo_combine",pool="pnfifo",quantile="0"} 0.291708
smrol_threshold_task_exec_ms{task="pnfifo_combine",pool="pnfifo",quantile="0.5"} 0.3098397629322033
smrol_threshold_task_exec_ms{task="pnfifo_combine",pool="pnfifo",quantile="0.9"} 2.152650766887626
smrol_threshold_task_exec_ms{task="pnfifo_combine",pool="pnfifo",quantile="0.95"} 4.880755386904117
smrol_threshold_task_exec_ms{task="pnfifo_combine",pool="pnfifo",quantile="0.99"} 12.096304627957473
smrol_threshold_task_exec_ms{task="pnfifo_combine",pool="pnfifo",quantile="0.999"} 22.42777184349927
smrol_threshold_task_exec_ms{task="pnfifo_combine",pool="pnfifo",quantile="1"} 38.860833
smrol_threshold_task_exec_ms_sum{task="pnfifo_combine",pool="pnfifo"} 471.20605099999966
smrol_threshold_task_exec_ms_count{task="pnfifo_combine",pool="pnfifo"} 392
smrol_threshold_task_exec_ms{task="pnfifo_sign",pool="pnfifo",quantile="0"} 0.30279100000000003
smrol_threshold_task_exec_ms{task="pnfifo_sign",pool="pnfifo",quantile="0.5"} 0.33303755796997925
smrol_threshold_task_exec_ms{task="pnfifo_sign",pool="pnfifo",quantile="0.9"} 2.1011819032351773
smrol_threshold_task_exec_ms{task="pnfifo_sign",pool="pnfifo",quantile="0.95"} 4.273785634121719
smrol_threshold_task_exec_ms{task="pnfifo_sign",pool="pnfifo",quantile="0.99"} 12.913845153330639
smrol_threshold_task_exec_ms{task="pnfifo_sign",pool="pnfifo",quantile="0.999"} 37.3114409337287
smrol_threshold_task_exec_ms{task="pnfifo_sign",pool="pnfifo",quantile="1"} 41.034667
smrol_threshold_task_exec_ms_sum{task="pnfifo_sign",pool="pnfifo"} 1851.4600319999995
smrol_threshold_task_exec_ms_count{task="pnfifo_sign",pool="pnfifo"} 1563
smrol_threshold_task_exec_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0"} 1.163042
smrol_threshold_task_exec_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0.5"} 2.3366072820908803
smrol_threshold_task_exec_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0.9"} 11.267246793842437
smrol_threshold_task_exec_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0.95"} 16.94037802384854
smrol_threshold_task_exec_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0.99"} 37.72413242729244
smrol_threshold_task_exec_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0.999"} 63.07345558257405
smrol_threshold_task_exec_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="1"} 83.175208
smrol_threshold_task_exec_ms_sum{task="pnfifo_verify_final",pool="pnfifo"} 7796.809322000001
smrol_threshold_task_exec_ms_count{task="pnfifo_verify_final",pool="pnfifo"} 1568

# HELP smrol_threshold_task_wait_ms Time threshold worker tasks wait before execution (ms)
# TYPE smrol_threshold_task_wait_ms summary
smrol_threshold_task_wait_ms{task="pnfifo_sign",pool="pnfifo",quantile="0"} 0.000334
smrol_threshold_task_wait_ms{task="pnfifo_sign",pool="pnfifo",quantile="0.5"} 0.022279239067282228
smrol_threshold_task_wait_ms{task="pnfifo_sign",pool="pnfifo",quantile="0.9"} 1.1294152211947255
smrol_threshold_task_wait_ms{task="pnfifo_sign",pool="pnfifo",quantile="0.95"} 1.7783749483022944
smrol_threshold_task_wait_ms{task="pnfifo_sign",pool="pnfifo",quantile="0.99"} 4.8023241576155575
smrol_threshold_task_wait_ms{task="pnfifo_sign",pool="pnfifo",quantile="0.999"} 10.44684483150229
smrol_threshold_task_wait_ms{task="pnfifo_sign",pool="pnfifo",quantile="1"} 15.632541999999999
smrol_threshold_task_wait_ms_sum{task="pnfifo_sign",pool="pnfifo"} 578.881803999999
smrol_threshold_task_wait_ms_count{task="pnfifo_sign",pool="pnfifo"} 1563
smrol_threshold_task_wait_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0"} 0.0012920000000000002
smrol_threshold_task_wait_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0.5"} 0.026186794627140547
smrol_threshold_task_wait_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0.9"} 0.9881705199936898
smrol_threshold_task_wait_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0.95"} 1.8981884749657771
smrol_threshold_task_wait_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0.99"} 5.141269330597383
smrol_threshold_task_wait_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="0.999"} 13.986603851760123
smrol_threshold_task_wait_ms{task="pnfifo_verify_final",pool="pnfifo",quantile="1"} 18.373250000000002
smrol_threshold_task_wait_ms_sum{task="pnfifo_verify_final",pool="pnfifo"} 599.0789120000001
smrol_threshold_task_wait_ms_count{task="pnfifo_verify_final",pool="pnfifo"} 1568
smrol_threshold_task_wait_ms{task="pnfifo_combine",pool="pnfifo",quantile="0"} 0.000792
smrol_threshold_task_wait_ms{task="pnfifo_combine",pool="pnfifo",quantile="0.5"} 0.014785622559641687
smrol_threshold_task_wait_ms{task="pnfifo_combine",pool="pnfifo",quantile="0.9"} 0.9570496527284266
smrol_threshold_task_wait_ms{task="pnfifo_combine",pool="pnfifo",quantile="0.95"} 1.8853245801044953
smrol_threshold_task_wait_ms{task="pnfifo_combine",pool="pnfifo",quantile="0.99"} 4.053983587964991
smrol_threshold_task_wait_ms{task="pnfifo_combine",pool="pnfifo",quantile="0.999"} 6.041788038462465
smrol_threshold_task_wait_ms{task="pnfifo_combine",pool="pnfifo",quantile="1"} 10.373375000000001
smrol_threshold_task_wait_ms_sum{task="pnfifo_combine",pool="pnfifo"} 139.37516499999998
smrol_threshold_task_wait_ms_count{task="pnfifo_combine",pool="pnfifo"} 392
smrol_threshold_task_wait_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0"} 0.001083
smrol_threshold_task_wait_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0.5"} 0.021500050010122833
smrol_threshold_task_wait_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0.9"} 1.0490657384267885
smrol_threshold_task_wait_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0.95"} 1.729271111378521
smrol_threshold_task_wait_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0.99"} 4.473181945403979
smrol_threshold_task_wait_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="0.999"} 9.156829573846817
smrol_threshold_task_wait_ms{task="pnfifo_verify_share",pool="pnfifo",quantile="1"} 9.930417
smrol_threshold_task_wait_ms_sum{task="pnfifo_verify_share",pool="pnfifo"} 569.2068760000004
smrol_threshold_task_wait_ms_count{task="pnfifo_verify_share",pool="pnfifo"} 1568
smrol_threshold_task_wait_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0"} 0.000959
smrol_threshold_task_wait_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0.5"} 0.0765431983227338
smrol_threshold_task_wait_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0.9"} 1.080150080877478
smrol_threshold_task_wait_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0.95"} 2.205821490656221
smrol_threshold_task_wait_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0.99"} 5.751726098656708
smrol_threshold_task_wait_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="0.999"} 13.368484095458628
smrol_threshold_task_wait_ms{task="verify_seq_order_batch",pool="seq_offload",quantile="1"} 16.293084
smrol_threshold_task_wait_ms_sum{task="verify_seq_order_batch",pool="seq_offload"} 191.8797919999999
smrol_threshold_task_wait_ms_count{task="verify_seq_order_batch",pool="seq_offload"} 392
