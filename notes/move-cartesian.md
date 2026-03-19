
```bash
curl -X POST http://127.0.0.1:8000/move/cartesian \
  -H "Content-Type: application/json" \
  -d '{
    "x": 300,
    "y": 0,
    "z": 400,
    "rx": 180,
    "ry": 0,
    "rz": 0,
    "vel": 10
  }'
```

```json
{
    "success":true,
    "dry_run":false,
    "robot_ip":"147.175.151.23",
    "command":"MoveCart",
    "desc_pos":[300.0,
                0.0,
                400.0,
                180.0,
                0.0,
                0.0
                ],
    "tool":0,
    "user":0,
    "vel":10.0,
    "error_code":0,
    "message":"Motion command accepted by robot controller."
}
```

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/robot/state' \
  -H 'accept: application/json'
```

```json
{
    "robot_ip":"147.175.151.23",
    "realtime_available":true,
    "enabled":1,
    "robot_mode":1,
    "program_state":1,
    "robot_state":1,
    "emergency_stop":0,
    "safety_stop":[0,0],
    "collision_state":0,
    "motion_done":1,
    "tool":0,
    "user":0,
    "main_error_code":0,
    "sub_error_code":0,
    "tcp_pose":[
        299.9983215332031,
        -0.0011581145226955414,
        520.0025024414062,
        -179.9999237060547,
        -0.00020459096413105726,
        0.000217550914385356
        ],
    "joint_pos":[
        19.87677001953125,
        -169.9049835205078,
        84.88581085205078,
        -4.980613708496094,
        -90.0,
        109.87654876708984
        ],
    "message":null
}
```

```bash
curl -X POST http://127.0.0.1:8000/move/cartesian \
  -H "Content-Type: application/json" \
  -d '{
    "x": 300,
    "y": 0,
    "z": 400,
    "rx": 180,
    "ry": 0,
    "rz": 0,
    "vel": 10
  }'
```

```json
{
    "success":true,
    "dry_run":false,
    "robot_ip":"147.175.151.23",
    "command":"MoveCart",
    "desc_pos":[300.0,
                0.0,
                400.0,
                180.0,
                0.0,
                0.0
                ],
    "tool":0,
    "user":0,
    "vel":10.0,
    "error_code":0,
    "message":"Motion command accepted by robot controller."
}
```

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/robot/state' \
  -H 'accept: application/json'
```

```json
{
    "robot_ip":"147.175.151.23",
    "realtime_available":true,
    "enabled":1,
    "robot_mode":1,
    "program_state":1,
    "robot_state":1,
    "emergency_stop":0,
    "safety_stop":[0,0],
    "collision_state":0,
    "motion_done":1,
    "tool":0,
    "user":0,
    "main_error_code":0,
    "sub_error_code":0,
    "tcp_pose":[
        300.0003967285156,
        -0.0004074531316291541,
        400.00189208984375,
        -179.9999237060547,
        -0.0002045906730927527,
        -1.320566295204273e-10
        ],
    "joint_pos":[
        19.87677001953125,
        -186.09425354003906,
        101.68336486816406,
        -5.588886737823486,
        -90.0,109.87677001953125
    ],
    "message":null
}
```

prečo identický command skončil s rôznym z (400 vs 520)?  
chcela som [300, 0, 520, -180, 0, 0] 
dostala som [300, 0, 520, -180, 0, 0]
chcela som zase [300, 0, 520, -180, 0, 0]  
dostala som [300, 0, 400, -180, 0, 0]  

TCP issue maybe ? (tool center point)
180 a -180 je vlastne to iste tu  

dorobila som endpoint na tool-state 

```json
{
  "robot_ip": "147.175.151.23",
  "active_tool": 0,
  "active_tcp_offset": [
    0,
    0,
    0,
    0,
    0,
    0
  ],
  "current_tool_coord": [
    0,
    0,
    0,
    0,
    0,
    0
  ],
  "tool_0_coord": [
    0,
    0,
    0,
    0,
    0,
    0
  ],
  "tool_1_coord": [
    0,
    0,
    120,
    0,
    0,
    0
  ],
  "message": null
}
```

tool 0 ma TCP [0, 0, 0, 0, 0, 0]
tool 1 ma TCP [0, 0, 120, 0, 0, 0]

tam je tych 120 mm
ale pouziva rn tool 0 ??