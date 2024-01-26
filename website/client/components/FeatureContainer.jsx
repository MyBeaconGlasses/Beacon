import Image from "next/image";

const FeatureContainer = ({ feature }) => {
  return (
    <div className="text-white bg-[rgba(84,84,84,0.18)] px-[1rem] py-[2rem] max-w-[360px] shadow-[inset_0px_2px_4px_0px_rgba(223,223,223,0.17)] rounded-[12px]">
      <Image src={feature.logo} />
      <div className="text-[24px] font-semibold mt-[0.5rem]">
        {feature.title}
      </div>
      <div className="text-[16px] font-regular text-[#9C9C9C] mt-[1rem]">
        {feature.description}
      </div>
    </div>
  );
};

export default FeatureContainer;
