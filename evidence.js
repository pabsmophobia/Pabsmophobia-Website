// Transform YouTube API items into the exact data structure expected by renderEvidence
const evidenceList = data.items
  .filter(item => item.snippet.title !== 'Private video' && item.snippet.title !== 'Deleted video')
  .map(item => {
    const snippet = item.snippet;
    const description = snippet.description || '';
    
    // Auto-detect status from description (#status:debunked or #debunked)
    let status = 'paranormal';
    if (description.toLowerCase().includes('#status:debunked') || description.toLowerCase().includes('#debunked')) {
      status = 'debunked';
    }

    // Extract location from #loc:Location Name or fallback to Location: Name
    let location = 'Field Telemetry';
    const locTagMatch = description.match(/#loc:([^\r\n#]+)/i);
    const locColonMatch = description.match(/Location:\s*([^\r\n#]+)/i);

    if (locTagMatch && locTagMatch[1]) {
      location = locTagMatch[1].trim();
    } else if (locColonMatch && locColonMatch[1]) {
      location = locColonMatch[1].trim();
    }

    return {
      title: snippet.title,
      description: description || 'No detailed log summary provided.',
      location: location,
      type: 'video',
      status: status,
      date: new Date(snippet.publishedAt).toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      }),
      mediaUrl: `https://www.youtube-nocookie.com/embed/${snippet.resourceId.videoId}`
    };
  });
