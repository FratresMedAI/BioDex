import traceback
try:
    from megadetector.detection import run_detector
    m = run_detector.load_detector("MDV5A")
    print("OK", type(m))
except Exception as e:
    traceback.print_exc()
