from uniulm_mensaparser import Canteen, get_plan, SimpleAdapter2, FsEtAdapter


if __name__ == "__main__":
    plan = get_plan(adapter_class=SimpleAdapter2)
    print(plan)

    plan = get_plan({Canteen.UL_UNI_Sued}, adapter_class=FsEtAdapter)
    print(plan)
