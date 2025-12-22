# Product Requirements Document

**Product Name:** Brain Radio – Personalized Focus Music Platform

## Overview and Purpose

Brain Radio is a user-personalized alternative to Brain.fm, providing a focus and relaxation music web application that curates tracks based on individual user preferences. The goal is to harness both human curation and AI intelligence to deliver functional music (music designed for concentration, meditation, sleep, etc.) tailored to each user's tastes and needs. Brain Radio will offer a simple, lightweight interface where users can play ambient and instrumental tracks that help them achieve mental states like deep focus or calm relaxation, without the distractions of typical music apps.

Unlike Brain.fm which generates music via AI algorithms, Brain Radio focuses on curated tracks and tagging. It will leverage existing high-quality tracks (e.g. creative commons music, user-provided audio, or licensed collections) and use a robust tagging system (metadata like mood, genre, energy level) to categorize them. AI comes into play by analyzing user behavior and preferences to recommend the right track or playlist at the right time. In essence, Brain Radio combines the reliability of known-good music (handpicked or community-vetted) with the personalization of AI-driven recommendations, resulting in an experience that feels both personal and effective for enhancing focus or relaxation.

## Goals and Objectives

- Deliver scientifically beneficial music experiences for focus, relaxation, sleep, and meditation similar to Brain.fm's promise of "music that affects you differently"[52]. The app should help users quickly enter a desired mental state (e.g., intense focus for work, or calm for sleep) by playing appropriate audio.
- Provide personalization: adapt to each user's preferences ("brain type"). Brain Radio will feature user profiles that learn over time. For example, if a user often skips high-energy tracks when trying to focus and favors piano-based ambient music, the system will favor those in recommendations. The aim is to offer "personalized music for your brain type", a feature Brain.fm also advertises[53], but do so using the user's explicit feedback and choices rather than proprietary AI generation.
- Keep the user interface minimal and distraction-free. A key selling point is a lightweight interface that avoids the clutter of traditional music apps (no endless feed, no video thumbnails, etc.). Brain Radio should be one-click simple: the user might just choose a mode (Focus, Relax, Sleep, etc.) and hit play, similar to Brain.fm's one-tap approach to modes[54]. This simplicity helps users avoid decision fatigue or rabbit-hole distractions (like getting sidetracked by browsing music instead of working)[55].
- Incorporate AI-driven recommendations ethically and transparently. Use open-source or permitted AI (or possibly OpenAI's API if allowed) to analyze tagging and user behavior to queue up tracks. The AI might also generate mixes or playlists on the fly by understanding what track sequences work well (e.g., gradually slowing tempo as the user nears bedtime). However, unlike purely generative solutions, Brain Radio's AI will work with a fixed library of tracks, ensuring the music quality is consistent and not jarring or overly novel (a criticism of fully generative music is it can have odd or distracting moments[56]). The product should strike a balance: automation with a human touch.
- Ensure the product is accessible and affordable. Brain Radio should be free to use (or one-time purchase) if possible, in contrast to subscription-only models. This addresses a common complaint about Brain.fm's cost barrier[57]. Brain Radio could be an open-source project users can self-host or run locally, ensuring that access to focus music isn't locked behind recurring fees.

## User Personas

### Focused Professional (Persona: Alex)

Alex is a software developer who struggles with maintaining concentration during long coding sessions. They currently use generic lo-fi playlists on YouTube but find themselves occasionally distracted by the platform. Alex wants a dependable, no-frills solution: just open an app, click "Focus Mode," and get 2 hours of uninterrupted background music that keeps them in the zone. Alex values Brain Radio's promise of purposeful music without distractions, and the personalization that learns their taste (maybe they prefer mellow electronic beats over classical). They will primarily use the "Focus" category and appreciate the ability to tag favorite tracks or mark which ones really helped them concentrate.

### Restful Mind (Persona: Bella)

Bella is a busy graduate student who also has trouble winding down at night. She's tried Brain.fm's sleep music during a trial and liked it, but didn't subscribe. She loves the idea of curated relaxation tracks that she doesn't have to assemble herself. Bella will use Brain Radio for relaxation breaks (a 10-minute meditation music during stress) and for falling asleep (perhaps a gentle piano or rain sound mix for 30 minutes). She values personalization too – for example, she finds white noise effective but ocean sounds distracting, so she wants the app to learn and favor certain kinds of sounds for her "Sleep" mode. Bella might also use "Meditation" mode for guided breathing sessions if available.

### Productivity Seeker (Persona: Chris)

Chris is a freelance designer who has ADHD. They heard that Brain.fm or similar AI music can help with ADHD focus. Chris uses Brain Radio as a tool to manage their attention – hitting Focus with high-energy electronic music for short sprints when they need a boost, or Relax with calm nature sounds when feeling anxious. Chris appreciates tagging because they might filter tracks by "no vocals" or "beta wave" if that tag is present. They are tech-savvy and might even contribute track suggestions or tag corrections to the open-source project. For Chris, Brain Radio is not just an app but a community-driven solution for better productivity.

## Features and Scope (MVP)

Brain Radio's Minimum Viable Product will include the core functionality needed to serve the above users:

### User Modes / Categories

At least four primary categories of music akin to Brain.fm's offerings – e.g. Focus, Relax, Sleep, Meditation (final names TBD). Each mode will have a curated list or playlist algorithm suited to that context. For MVP, these modes can be hardcoded playlists or simple algorithms (shuffle through tagged tracks). For example, Focus mode might cycle through uptempo instrumental tracks tagged "focus" or "energizing", while Sleep mode might play slower, ambient sounds tagged "sleep" or "ambient".

### Curated Track Library

An initial library of tracks (perhaps 50-100 tracks) that are either original, Creative Commons, or licensed for use. Each track will have metadata:

- Title, Artist (if applicable)
- Tags (mood: upbeat, calm; purpose: focus, relax; genre: classical, electronic; additional: instruments, BPM, etc.)
- Duration, and maybe an intensity rating.

The MVP can store these tracks on the server or allow users to upload their own tracks (the latter could be a stretch goal for MVP depending on complexity). The important part is having enough content to provide variety but all of it fitting the functional purpose (no highly distracting pieces).

### Tagging & Filtering

The system should support filtering tracks by tags. This may not be an exposed UI in MVP (we might just use it internally for mode playlists), but it's crucial for the recommendation engine. For instance, Focus mode might explicitly select tracks with tag "focus" or "energetic" and not "sleep". In later versions, we might allow advanced users to customize what tags they want or don't want in a session (e.g., exclude "rain sounds" if they dislike them).

### AI Recommendation Engine

A simple recommendation system that observes user interactions:

- If a user skips a track quickly, treat that as a negative signal for that track in that context.
- If a user favorites a track (we will have a favorite/like button), boost similar tracks (with overlapping tags or same artist).
- Optionally, a "smart shuffle" that reorders upcoming tracks based on what the user has enjoyed historically. For MVP, this could be rule-based or a basic collaborative filter, but since personalization is a key differentiator, we should include at least a rudimentary AI component. If allowed, we might use OpenAI's API to classify tracks or generate embeddings for tracks descriptions to compute similarity, but since we likely rely on tags and known metadata, a simpler heuristic approach could suffice (open source libraries for recommendation can be used). The outcome is that over time the app feels more tailored – e.g., Bella's Sleep mode gradually shifts to mostly piano ambient pieces if that's what she listens to fully.

### Lightweight Web Interface

A clean web UI (could be a single-page application or server-rendered pages) with the following elements:

- Mode selection buttons or tabs (Focus, Relax, etc.).
- A Play/Pause control and Skip button.
- Track display: show current track title, maybe an image or waveform.
- A way to like/favorite the current track.
- Volume control.
- (Optional for MVP) Timer or duration if needed (some might want a session timer).
- (Optional) Login/profile if we want to save preferences per user – for MVP, we might skip authentication and just use local storage or a cookie to save favorites, to avoid backend complexity. However, profiles are important for personalization, so maybe a simple login via Google or email could be in scope if not too time-consuming.

The UI should be responsive and minimalistic – think along the lines of a small media player with a few buttons, not a busy dashboard. Brain.fm's interface is noted as not flashy and helps avoid distraction[55]; we will emulate that philosophy.

### Audio Playback and Transition

Continuous playback of tracks with smooth transitions (gapless or crossfade if possible) because abrupt silence can break focus. We might include a slight cross-fade or blending between tracks in focus mode. For sleep mode, possibly an endless loop or a fade-out at the end. Technically, we'll likely use HTML5 Audio or Web Audio API to handle playback in the browser. Ensure that playback continues with screen off (for mobile users listening on phone) – maybe a PWA or at least background audio support.

### Platform and Deployment

The MVP will be a web app delivered via a single Docker container (see Acceptance Criteria). This includes a backend (if needed for serving tracks or storing preferences) and the frontend. For MVP, the backend could be very light – maybe just a static file server if no login, or a simple API to record likes and fetch recommendations. We might decide on a tech stack such as Python Flask or Node.js for simplicity, plus a lightweight database or even just in-memory storage for user data if not persistent. The emphasis is on making it open source friendly and easy to deploy (e.g., host it on one's own machine or a small cloud instance).

## Out-of-Scope (for MVP)

It's important to clarify what we are not doing in the first version:

- Mobile native apps (iOS/Android) – not in MVP, but the web app should be mobile-web-friendly.
- AI-generated music: We will not generate new audio content via AI in MVP; we rely on existing tracks. The complexity of generative audio and ensuring quality is beyond scope.
- Large music library integration: We won't integrate Spotify or other proprietary libraries due to cost and complexity. All content will be either bundled or user-provided small scale. No streaming from third-party services in MVP.
- Advanced user accounts or social features: MVP may have basic login at most. No social network, sharing playlists, etc. Possibly in future if community grows.
- Monetization: MVP is free. No payment or subscription system initially.
- Neurofeedback or hardware integration: Some focus music products use biofeedback (like reading brainwaves). We will not incorporate any external hardware; Brain Radio is purely software-based recommendation and playback.

## Technical Constraints and Considerations

### Use of OpenAI APIs

The product can use OpenAI (or similar) for recommendations if needed (for instance, using GPT-4 to classify user feedback or to categorize a new track's mood from its description). However, since this is an open-source project, reliance on a paid API should be optional. We aim for an open-source only solution if possible, perhaps using local inference or simpler algorithms. That said, if AI features (like natural language playlist requests: "play me something to help with creative thinking") are desired, OpenAI's API could be toggled on with a key. As a baseline, Brain Radio's core should function without requiring closed APIs – ensuring anyone can deploy it without needing an API key (they just won't get the fancy AI suggestions, maybe just random or tag-based suggestions).

### Licensing of Music

All curated tracks must be legally usable (e.g., public domain, CC0, CC-BY with attribution, or properly licensed). This is a constraint to avoid legal issues. The PRD should emphasize track curation must respect copyright. Possibly involve community contributions of CC-licensed content. We might include attribution for tracks if required by license, so UI should accommodate showing that (maybe in a credits modal or on track hover).

### Performance

The app should be lightweight – able to load quickly in a browser and not consume excessive memory (especially since some users will run it while working on other tasks). We must compress audio appropriately and possibly allow users to choose a lower streaming quality if bandwidth is a concern. But given MVP likely runs locally or on a small server, we assume moderate use.

### Personalization Algorithm

Must respect privacy. If any user data (like listening habits) is stored, clarify that it's local or self-hosted. If this becomes a service, ensure GDPR compliance (but as open-source, probably user data stays with user).

### Multi-platform Audio Issues

Ensure compatibility with common browsers. Possibly use standard media formats (MP3 or OGG). We may need to consider how to keep audio playing if the user switches apps (for mobile, may need some PWA or media session API usage so it doesn't stop).

## Key Features Detailed (MVP)

### Mode Selection & Playback

Users select one of the four modes (Focus, Relax, Sleep, Meditation). Once selected, the app immediately starts playing a track from that mode's playlist. Playback continues automatically to the next recommended track when one ends. Users can pause or skip at any time. The transition between tracks is smooth (no harsh stops).

### Favorite Tracks

Users can mark a track as favorite. The system logs this (e.g., in local storage or user profile). Favoriting influences recommendations – those tracks might appear more often or a "Favorites mix" mode could be available in the future. It also simply provides the user a list of their favorites (so they can manually revisit tracks they liked via a Favorites list page, if we implement one).

### Basic Recommendation Logic

The app adapts in real-time:

- If a user skips a track within, say, 15 seconds, consider that track a "bad fit" for the current mode/user. The algorithm will de-prioritize similar tracks. (Similarity can be inferred from tags or track attributes.)
- If a user listens to a track fully (or repeats it), mark it as a good fit. Over time, this could be refined into a rating system. For MVP, a simple approach: maintain a score per track per user that goes up when fully listened or liked, and down when quickly skipped. Use that to sort the playlist order (most liked by that user in mode play sooner).

### Interface Simplicity

Minimal controls as described. Possibly a background or subtle visual but nothing too attention-grabbing. Maybe the background color or theme changes slightly per mode (blue for Focus, green for Relax, etc.) for a bit of mood setting.

### Documentation & Help

As an open project, include a README (outside this PRD) for how to add new tracks or tags, how the recommendation works, etc. But within the app, also have a "About Brain Radio" section explaining briefly that "This app plays music to help you focus or relax. It learns your preferences as you use it. Use the like button to mark favorites, and skip any tracks that aren't working for you." The goal is to manage user expectations and encourage them to interact (like/skips) so the personalization can work.

## Future Enhancements (beyond MVP, not required now but considered)

- More refined AI recommendations: e.g. using NLP to let user type "I want nature sounds with piano" and the system creating a quick custom playlist if tracks match. Or cluster tracks by acoustic similarity (maybe using ML audio analysis).
- User-generated tags or community tagging if open to crowdsource.
- Mobile apps or offline download of tracks.
- Integration with smart assistants (tell Alexa/Google to start Brain Radio focus mode).
- Generative soundscapes as an optional feature for advanced users.
- Social sharing of favorite focus tracks or playlist times (share a "focus session" link).
- Additional modes like "Memory" (for memorization tasks, maybe classical music) or "Creative" (slightly more dynamic music for creativity spurts).
- Multi-user support for small teams or offices (synchronizing music for group sessions).

## Constraints

### Open Source Only (if required)

We aim to rely on open libraries for everything. For audio playback – HTML5 is built-in. For recommendations – libraries like Surprise or simple in-house logic. If we include any AI model, prefer open ones (maybe a lightweight transformer for tag-based similarity, or use an open API like HuggingFace inference if needed).

### Hardware

No specialized hardware needed; should run on common laptops or small server (like Raspberry Pi for self-host maybe).

### Timeline

As an MVP built by autonomous coding agents, we must keep the scope manageable to be delivered quickly (in possibly days or a couple of weeks of agent work). That's why features like login might be simplified or skipped to avoid complexity like setting up databases, etc. The PRD emphasizes features that can be built with limited integration pain.

## Success Criteria (Product)

Brain Radio is successful if a user can, with minimal clicks, get into a session of music that genuinely helps their focus or relaxation, and the app progressively tunes itself to the user's taste. A qualitative measure is user satisfaction (perhaps measured by them continuing to use it regularly, or reporting improved focus). Quantitatively, we might track skip rates – if over time the skip rate decreases for a user, it means the app is learning their preferences. Also, favorites added is a positive engagement sign. For the open-source project, success includes community adoption: others might add tracks or improve the algorithm. We'll also validate the system doesn't just blindly mimic Brain.fm but offers its own twist: user control and transparency in how music is chosen, which some users might prefer over a black-box AI DJ.

Brain Radio positions itself as your personalized radio for the brain – taking the idea of Brain.fm (AI + music for cognitive states) but making it personal, transparent, and accessible to everyone without heavy cost or closed systems. The MVP outlined will set the foundation for this vision by focusing on core modes, a solid curated track base, and learning from user feedback through tagging and simple AI logic.
