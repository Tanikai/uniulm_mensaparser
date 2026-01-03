from uniulm_mensaparser import SimpleAdapter2, get_plan

if __name__ == "__main__":
    plan = get_plan(adapter_class=SimpleAdapter2)
    print(plan)
