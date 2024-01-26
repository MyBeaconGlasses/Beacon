import FeatureContainer from "./FeatureContainer";

import Aurora from "../assets/images/aurora-features.png";
import Brain from "../assets/images/feature-logos/Brain.png";
import Eye from "../assets/images/feature-logos/eye.png";
import Window from "../assets/images/feature-logos/Window.png";
import Hand from "../assets/images/feature-logos/Hand.png";
import Question from "../assets/images/feature-logos/Question.png";
import Lightbulb from "../assets/images/feature-logos/Lightbulb.png";

import Image from "next/image";

const featureList = [
  {
    title: "Eye Tracking",
    description:
      "With state-of-the-art infrared sensors, our smart glasses provide unparalleled control through natural eye movements. ",
    logo: Eye,
  },
  {
    title: "Heads-Up Display",
    description: "Our HUD offers real-time overlays of information.",
    logo: Window,
  },
  {
    title: "Agent/Expert Systems",
    description:
      "Serve as an extension of your short-term/long-term memory, manage summarization histories, and assist in learning.",
    logo: Brain,
  },
  {
    title: "Vision + Text Questions",
    description:
      "Equipped with advanced OCR and reverse image search capabilities.",
    logo: Question,
  },
  {
    title: "Remote Controlling & Hand Gestures",
    description:
      "Beyond eye tracking, our gesture control allows for a hands-free experience. ",
    logo: Hand,
  },
  {
    title: "Core Technologies",
    description:
      "Secret secret stuff that Bill explicitly told me not to spill.",
    logo: Lightbulb,
  },
];

const Features = () => {
  return (
    <div className="relative w-full flex justify-center py-[16rem] text-white md:px-[4rem]">
      <Image
        src={Aurora}
        alt="Background image"
        quality={100}
        className="absolute object-cover w-full z-[-1] top-0"
      />
      <div className="max-w-[1200px] flex flex-col items-center">
        <div className="text-[36px] font-bold">Features</div>
        <div className="flex flex-wrap md:justify-between justify-center gap-y-6 mt-[4rem]">
          {featureList.map((feature, index) => {
            return <FeatureContainer key={index} feature={feature} />;
          })}
        </div>
      </div>
    </div>
  );
};

export default Features;
