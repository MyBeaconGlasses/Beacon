import Aurora from "../assets/images/Aurora.png";
import Glasses from "../assets/images/glasses.png";

import Image from "next/image";

const Hero = () => {
  return (
    <div className="text-white w-full flex justify-center items-center py-[16rem]">
      <Image
        src={Aurora}
        alt="Background image"
        quality={100}
        className="absolute object-cover w-full z-[-1] top-0"
      />

      <div className="flex flex-col">
        <Image src={Glasses} alt="Background image" quality={100} width={600} />
        <div className="text-center flex flex-col items-center mt-[8rem]">
          <div className="font-bold text-[84px]">Beacon</div>
          <div className="font-medium text=[16px]">
            The OS for Everything Around You
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
