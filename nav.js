document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector("header");
  const navContainer = document.querySelector("header nav");
  if (!navContainer) return;

  // Normalize current pathname
  let rawPath = window.location.pathname.toLowerCase().replace(/\/$/, ""); // Strip trailing slash
  let currentPage = rawPath.split("/").pop().split("?")[0].split("#")[0];

  // Default to index.html for root URLs
  if (!currentPage || currentPage === "" || currentPage === "pabsmophobia-website") {
    currentPage = "index.html";
  }

  // Ensure .html extension for uniform matching if route is extensionless
  if (!currentPage.endsWith(".html")) {
    currentPage += ".html";
  }

  // Navigation Links Definition
  const navItems = [
    { name: "Home", link: "index.html" },
    { name: "About Us & Team", link: "team.html" },
    { name: "Events", link: "events.html" },
    { name: "Blogs & Newsletters", link: "blog.html" },
    { name: "Evidence", link: "evidence.html" },
    { name: "Contact", link: "contact.html" },
    { name: "Links", link: "links.html" }
  ];

  // Generate HTML links and apply active class dynamically
  navContainer.innerHTML = navItems.map(item => {
    // Active if exact filename match, or if viewing post.html under Blogs
    const isActive = (currentPage === item.link || (item.link === 'blog.html' && currentPage === 'post.html')) 
      ? 'class="active"' 
      : '';

    return `<a href="${item.link}" ${isActive}>${item.name}</a>`;
  }).join("");

  // Mobile Menu Toggle Logic
  if (header && !document.querySelector('.mobile-nav-toggle')) {
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'mobile-nav-toggle';
    toggleBtn.setAttribute('aria-label', 'Toggle Navigation');
    toggleBtn.innerHTML = '&#9776;'; // Hamburger icon
    toggleBtn.style.cssText = `
      display: none;
      background: none;
      border: none;
      color: #fff;
      font-size: 1.8rem;
      cursor: pointer;
      padding: 0.25rem 0.5rem;
    `;

    // Append button inside header
    header.appendChild(toggleBtn);

    // Toggle menu visibility on click
    toggleBtn.addEventListener('click', () => {
      navContainer.classList.toggle('nav-open');
    });
  }
});
