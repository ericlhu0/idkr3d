from PIL import Image
from lang_sam import LangSAM
from lang_sam.utils import draw_image
import supervision as sv
import cv2
import numpy as np
import argparse
def crop_handle_from_results(image, results, score_threshold=0):
  cropped_handles = []

  for result in results:
    boxes = result.get("boxes", [])
    scores = result.get("scores", [])
    masks = result.get("masks", [])
    labels = result.get("labels", [])

    for i, score in enumerate(scores):
      if score >= score_threshold:
        x1, y1, x2, y2 = map(int, boxes[i])
        cropped = image[y1:y2, x1:x2]
        if len(masks) > 0 and i < len(masks) and "curved" in labels[i]:
          print(labels[i])
          mask = masks[i][y1:y2, x1:x2]
          # mask = cv2.resize(mask, (x2 - x1, y2 - y1)) #mask resize
          mask = (mask > 0.5).astype(np.uint8) 
          cropped = cropped * mask[:, :, np.newaxis] 
          cropped_handles.append(cropped)

  return cropped_handles


if __name__ == '__main__':
  model = LangSAM()
  parser = argparse.ArgumentParser(description="Handle Detection")
  parser.add_argument('--image_path', type=str, default='kettle.png', help="Path to the input image.")
  args = parser.parse_args()
  image_pil = Image.open(args.image_path).convert("RGB")
  text_prompt = "Handle of a cylindrical mug"
  results = model.predict([image_pil], [text_prompt])
  
  
  # image_array = np.asarray(image_pil)
  # output_image = draw_image(
  #     image_array,
  #     results["masks"],
  #     results["boxes"],
  #     results["scores"],
  #     results["labels"],
  # )
  # print(results["labels"])
  # output_image = Image.fromarray(np.uint8(output_image)).convert("RGB")
  # output_image.save(args.image_path + " cropped.png")
      
  
        
  image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
  cropped_handles = crop_handle_from_results(image_cv, results)
  print(len(cropped_handles), len(results))
  for idx, handle in enumerate(cropped_handles):
    print(f"wrote {idx + 1}")
    cv2.imshow(f"Cropped Handle {idx + 1}", handle)
    cv2.imwrite(f"{args.image_path} handle_{idx + 1}.png", handle) 

    edges = cv2.Canny(handle, threshold1=200, threshold2=400, apertureSize=3)

    cv2.imwrite(args.image_path + "outline.png", edges)