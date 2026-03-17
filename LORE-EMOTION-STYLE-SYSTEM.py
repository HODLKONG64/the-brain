class EmotionBox:
    def __init__(self):
        self.emotions = {} 

    def add_emotion(self, name, intensity):
        self.emotions[name] = intensity

    def get_emotions(self):
        return self.emotions


class EmotionPicker:
    def __init__(self, emotion_box):
        self.emotion_box = emotion_box

    def pick_emotion(self):
        # Logic to pick an emotion based on some criteria
        return max(self.emotion_box.get_emotions(), key=self.emotion_box.get_emotions().get)


class StylePromptBuilder:
    def __init__(self, base_prompt):
        self.base_prompt = base_prompt

    def build_prompt(self, emotion):
        return f"{self.base_prompt} with {emotion} flavor."


def main():
    emotion_box = EmotionBox()
    emotion_box.add_emotion('joy', 10)
    emotion_box.add_emotion('sadness', 5)
    
    picker = EmotionPicker(emotion_box)
    selected_emotion = picker.pick_emotion()

    prompt_builder = StylePromptBuilder("Write a story")
    final_prompt = prompt_builder.build_prompt(selected_emotion)

    print(final_prompt)


if __name__ == "__main__":
    main()