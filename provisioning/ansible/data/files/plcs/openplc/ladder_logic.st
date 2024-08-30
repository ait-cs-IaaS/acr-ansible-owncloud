PROGRAM Shift
  VAR
    power AT %IW0 : UINT;
    target_power AT %IW1 : UINT;
    field_current AT %IW2 : UINT;
    flow_rate AT %IW3 : UINT;
    generator_velocity AT %IW4 : UINT;
    grid_voltage AT %IW5 : UINT;
    grid_frequency AT %IW6 : UINT;
    shutdown AT %IX0.0 : BOOL;
    target_power_command AT %QW0 : UINT;
    shutdown_command AT %QX0.0 : BOOL;
  END_VAR

  power := power;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : Shift;
  END_RESOURCE
END_CONFIGURATION
