# jarvis

plugin-based command router. third rebuild. this time it's actually a plugin
system instead of one file with a hundred `if` statements — the whole point
of the rewrite.

## run it

```
python main.py
```

no dependencies required for text mode. try:

```
> what time is it
> note: buy a new charger
> notes
> calc 12 * (4 + 1)
> system info
> help
```

## how it's put together

- **core/plugin_base.py** — the `Plugin` interface. two methods:
  `can_handle(text, ctx)` and `handle(text, ctx)`.
- **core/plugin_manager.py** — scans `plugins/` at startup and instantiates
  anything that subclasses `Plugin`. drop a new file in, subclass `Plugin`,
  it's picked up automatically — no registry to edit.
- **core/router.py** — asks each plugin in turn "can you handle this?", uses
  the first one that says yes. if nothing claims it and an LLM fallback
  plugin is registered (see `plugins/llm_plugin.py`), that gets the last
  shot before giving up.
- **core/config.py** — environment-variable config, no config file format.
- **plugins/** — `time`, `notes` (json-persisted to `data/notes.json`),
  `calc` (ast-based, no `eval()`), `system` (read-only info), `llm`
  (optional fallback, needs `ANTHROPIC_API_KEY`).

## adding a plugin

```python
# plugins/weather_plugin.py
from core.plugin_base import Plugin, Context

class WeatherPlugin(Plugin):
    name = "weather"
    description = "'weather' — not actually wired to anything yet"

    def can_handle(self, text: str, ctx: Context) -> bool:
        return "weather" in text.lower()

    def handle(self, text: str, ctx: Context) -> str:
        return "no weather api hooked up, this is just a demo plugin."
```

that's it. no registration step — `plugin_manager` finds it on the next run.

## enabling the llm fallback

```
export ANTHROPIC_API_KEY=sk-...
python main.py
```

anything no other plugin recognizes gets sent to the api instead of a flat
"i don't understand." the call is a plain `urllib` request (see
`plugins/llm_plugin.py`) so there's no SDK dependency — swap in the real
`anthropic` package if you'd rather have retries/streaming/etc. for free.

## voice mode (not wired up here)

this environment has no mic or speaker to test against, so voice input/output
isn't implemented — but nothing in `core/` or `plugins/` assumes text came
from a keyboard. to add it:

1. `pip install SpeechRecognition pyttsx3 pyaudio`
2. in `main.py`, replace the `input("> ")` call with a
   `speech_recognition.Recognizer().recognize_google(...)` call that returns
   text the same way `input()` does.
3. wrap `router.route()`'s return value in `pyttsx3.speak(...)` instead of
   `print(...)`.

everything downstream of "here's a string the user said" is unchanged.

## what got cut

no actual OS automation (no clicking things, no opening apps) — a voice
assistant that pokes at your desktop by default is a bigger trust surface
than a portfolio demo should ask for. `system_plugin.py` is read-only on
purpose. if you want that back, it's a plugin like any other; just be
deliberate about what it's allowed to touch.
