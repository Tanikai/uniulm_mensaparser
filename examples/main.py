from uniulm_mensaparser import get_plan, SimpleAdapter2

if __name__ == "__main__":
    plan = get_plan(adapter_class=SimpleAdapter2)
    print(plan)
