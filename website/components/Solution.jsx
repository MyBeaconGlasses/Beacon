import Image from "next/image";

import Glasses from "../assets/images/glasses.png";

const Solution = () => {
  return (
    <div id="solution" className="text-white flex flex-col lg:flex-row justify-between items-center lg:space-x-[6rem] space-y-[6rem] lg:space-y-0 w-full py-[16rem] md:px-[4rem] px-[1rem] max-w-[1200px] mt-[1rem]">
      <div>
        <div className="inline font-bold bg-gradient-to-r from-[#6497E3] via-[#976FEB] to-[#E86FC6] text-transparent bg-clip-text">
          SOLUTION
        </div>
        <div className="text-[32px] font-bold">Introducing Beacon</div>
        <div>
          Our glasses redefine wearable technology by seamlessly merging the
          digital with the physical. Equipped with essential components like a
          camera, microphone, and speaker, and complemented by a user-friendly
          Webapp, they offer an intuitive, immersive experience, bridging the
          gap between what you know and what you're yet to discover.
        </div>
      </div>
      <Image src={Glasses} />
    </div>
  );
};

export default Solution;
