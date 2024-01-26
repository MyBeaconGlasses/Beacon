const Nav = () => {
  return (
    <div className="w-full flex justify-center items-center gap-16 font-medium text-white text-[16px] py-8 absolute">
      <div className="bg-[rgba(84,84,84,0.18)] px-[1rem] py-[0.5rem] max-w-[360px] shadow-[inset_0px_2px_4px_0px_rgba(223,223,223,0.17)] rounded-[16px]">
        Home
      </div>
      <div>About</div>
      <div>Solution</div>
      <div>Features</div>
      <div>Contact</div>
    </div>
  );
};

export default Nav;
