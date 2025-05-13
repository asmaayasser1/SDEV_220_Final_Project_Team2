// ================================================
// File: search.js
// Project: Healthy Foods Store - Final Project
// Description: JavaScript file to handle live product filtering and search functionality
// Author(s): Team 2 - asmaayasser1 and collaborators
// Date: May 2025
// ================================================



// static/search.js (TB)

document.addEventListener('DOMContentLoaded', () => {
    const searchBar = document.getElementById('search-bar');
    const cards     = Array.from(document.querySelectorAll('.product-card'));
  
    // debounce utility that limits how often the filter runs consecutively. (TB)
    let timeout = null;
    function debounce(fn, delay = 150) {
      clearTimeout(timeout);
      timeout = setTimeout(fn, delay);
    }
  
    searchBar.addEventListener('input', (e) => {
      const term = e.target.value.toLowerCase().trim();
  
      debounce(() => {
        cards.forEach(card => {
          const text = card.textContent.toLowerCase();
          card.style.display = text.includes(term) ? '' : 'none';
        });
      });
    });
  });
  
