from youtubesearchpython import VideosSearch

def search_youtube(topic):
    videos_search = VideosSearch(topic, limit = 10)  # Limit to 10 results
    results = videos_search.result()

    video_links = []
    for video in results['result']:
        video_links.append(f"https://www.youtube.com/watch?v={video['id']}")

    return video_links

# Example usage:
topic = "llama 3.1"
links = search_youtube(topic)
for link in links:
    print(link)
