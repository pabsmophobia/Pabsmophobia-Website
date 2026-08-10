document.addEventListener("DOMContentLoaded", () => {
  const navContainer = document.querySelector("header nav");
  if (!navContainer) return;

  // Get current HTML filename (default to index.html if root)
  let currentPage = window.location.pathname.split("/").pop();
  
  // Handle GitHub Pages where pathname might be empty or just /
  if (!currentPage || currentPage === "") {
    currentPage = "index.html";
  }
  
  // Remove query string if present
  currentPage = currentPage.split("?")[0];

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

  // Generate HTML links and apply active class automatically
  navContainer.innerHTML = navItems.map(item => {
    // Check if current page matches link or if viewing post.html under blogs
    const isActive = (currentPage === item.link || (item.link === 'blog.html' && currentPage === 'post.html')) 
      ? 'class="active"' 
      : '';
    return `<a href="${item.link}" ${isActive}>${item.name}</a>`;
  }).join("");
});
