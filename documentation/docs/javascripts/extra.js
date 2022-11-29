const app = () => {
  var darkModeMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  const handleDarkmode = (e) => {
    var darkModeOn = e.matches; // true if dark mode is enabled
    var favicon = document.querySelector('link[rel="icon"]'); // get favicon.ico element
    if (!favicon) {
      return; // where are our favicon elements???
    }
    // replace icons with dark/light themes as appropriate
    if (darkModeOn) {
      favicon.href = "/images/cosmian-favicon-white.png";
    } else {
      favicon.href = "/images/cosmian-favicon-black.png";
    }
  };
  handleDarkmode(darkModeMediaQuery);

  const icons = [
    "/icons/home.svg",
    "/icons/lock.svg",
    "/icons/chip.svg",
    "/icons/keyring.svg",
  ];
  // Get icons
  const addIcons = () => {
    const baseurl = document.location.origin;
    const navList = document.querySelectorAll(".md-nav--primary > ul > li");
    navList.forEach((node, index) => {
      const img = `<object type="image/svg+xml" data=${baseurl}${icons[index]} width="18" height="18"><img src=${baseurl}${icons[index]} /></object>`;
      if (index === 0) {
        const a = node.querySelector("a.md-nav__link");
        a.innerHTML = img + a.innerHTML;
      } else {
        const label = node.querySelector("label.md-nav__link");
        label.innerHTML = img + label.innerHTML;
      }
    });
  };
  addIcons();
};
app();
