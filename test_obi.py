from obi.sdk.core import OBIContext

print("=== OBI Reasoning Example ===\n")

# Create context
ctx = OBIContext(confidence_threshold=0.954)
print(f"Context: {ctx}\n")

# Example 1: Safe driving scenario
print("--- Example 1: Safe Driving ---")
safe_state = ctx.probe_internal({
    "speed_mph": 30,
    "distance_m": 150,
    "friction": 0.7,
    "obstacle": "cyclist"
})
safe_result = ctx.infer(safe_state)
print(safe_result)

print("\n--- Example 2: Emergency Braking ---")
emergency_state = ctx.probe_internal({
    "speed_mph": 65,
    "distance_m": 50,
    "friction": 0.45,  # wet road
    "obstacle": "cyclist"
})
emergency_result = ctx.infer(emergency_state)
print(emergency_result)

print("\n✓ OBI reasoning complete")
