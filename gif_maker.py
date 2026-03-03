import os
from PIL import Image

# 🔹 JPG 파일이 있는 폴더 경로
input_folder = "./replay_frames_2"

# 🔹 저장할 GIF 파일 이름
output_gif = "output_2.gif"

# 🔹 프레임 지속 시간 (밀리초)
duration = 500  # 0.5초

# 🔹 반복 여부 (0 = 무한 반복)
loop = 0

# JPG 파일 목록 가져오기 (이름순 정렬)
jpg_files = sorted([
    f for f in os.listdir(input_folder)
    if f.lower().endswith(".png")
])

# 이미지 열기
images = []
for file in jpg_files:
    img_path = os.path.join(input_folder, file)
    img = Image.open(img_path)
    images.append(img)

# GIF 저장
if images:
    images[0].save(
        output_gif,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=loop
    )
    print("GIF 생성 완료:", output_gif)
else:
    print("JPG 파일이 없습니다.")