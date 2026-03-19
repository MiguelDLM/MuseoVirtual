window.addEventListener('load', () => {
  if (window.Reveal) {
    if (Reveal.isReady()) {
      initTimeline();
    } else {
      Reveal.on('ready', initTimeline);
    }
  }
});

function initTimeline() {
  const container = document.createElement('div');
  container.className = 'custom-timeline-container';
  
  const track = document.createElement('div');
  track.className = 'custom-timeline-track';
  container.appendChild(track);

  const progress = document.createElement('div');
  progress.className = 'custom-timeline-progress';
  track.appendChild(progress);

  // Get all slide elements
  const slides = Reveal.getSlides();
  
  slides.forEach((slide, index) => {
    // Try to find a heading in the slide
    const heading = slide.querySelector('h1, h2, h3, h4');
    let title = '';
    
    // Check if it's the title slide (first slide usually has class "title-slide")
    if (index === 0 && slide.classList.contains('title-slide')) {
      const titleEl = slide.querySelector('.title');
      title = titleEl ? titleEl.innerText.trim() : 'Inicio';
    } else if (heading) {
      title = heading.innerText.trim();
    } else {
      title = `Diapositiva ${index + 1}`;
    }

    const milestone = document.createElement('div');
    milestone.className = 'custom-timeline-milestone';
    
    // Store indices for navigation
    const indices = Reveal.getIndices(slide);
    milestone.dataset.h = indices.h;
    if (indices.v !== undefined) {
      milestone.dataset.v = indices.v;
    }
    
    const dot = document.createElement('div');
    dot.className = 'custom-timeline-dot';
    
    const label = document.createElement('div');
    label.className = 'custom-timeline-label';
    // Shorten title if too long
    label.innerText = title.length > 25 ? title.substring(0, 25) + '...' : title;
    // Add tooltip for full title
    label.title = title;

    milestone.appendChild(dot);
    milestone.appendChild(label);
    
    milestone.addEventListener('click', () => {
      Reveal.slide(parseInt(milestone.dataset.h), parseInt(milestone.dataset.v || 0));
    });

    track.appendChild(milestone);
  });

  // Append to the reveal container
  const revealContainer = document.querySelector('.reveal');
  if (revealContainer) {
    revealContainer.appendChild(container);
  } else {
    document.body.appendChild(container); // Fallback
  }

  // Update classes initially
  updateTimelineProgress();

  // Listen to slide changes
  Reveal.on('slidechanged', updateTimelineProgress);
}

function updateTimelineProgress() {
  const currentSlide = Reveal.getCurrentSlide();
  const slides = Reveal.getSlides();
  const currentIndex = slides.indexOf(currentSlide);
  
  const milestones = document.querySelectorAll('.custom-timeline-milestone');
  const total = milestones.length;
  
  if (total <= 1) return;

  milestones.forEach((m, i) => {
    if (i === currentIndex) {
      m.className = 'custom-timeline-milestone active';
    } else if (i < currentIndex) {
      m.className = 'custom-timeline-milestone completed';
    } else {
      m.className = 'custom-timeline-milestone';
    }
  });

  // Update progress bar width
  const progressPercent = (currentIndex / (total - 1)) * 100;
  const progressLine = document.querySelector('.custom-timeline-progress');
  if (progressLine) {
    progressLine.style.width = `${progressPercent}%`;
  }
}
