# # src/vigilancia_prospectiva/pipelines.py
# class NormalizePipeline:
#     def process_item(self, item, spider):
#         # elimina duplicados y vacíos
#         for k in ("h1", "paragraphs"):
#             if isinstance(item.get(k), list):
#                 seen, out = set(), []
#                 for t in item[k]:
#                     if t and t not in seen:
#                         seen.add(t); out.append(t)
#                 item[k] = out
#         return item
