import os
import xml.etree.ElementTree as ET
import pickle
import traceback

def parse_voc_annotation(ann_dir, img_dir, cache_name, labels=[]):
    print('ACA ESTA ENTRANDO')
    print('#'*20 + '\n\nSTARTING TO PARSE ANNOTATIONS\n\n'  + '#' * 20)
    if os.path.exists(cache_name) and False:
        with open(cache_name, 'rb') as handle:
            cache = pickle.load(handle)
        all_insts, seen_labels = cache['all_insts'], cache['seen_labels']
    else:
        all_insts = list()
        seen_labels = dict()

        print('Annotations to be read: ', len(os.listdir(ann_dir)))
        for ann in sorted(os.listdir(ann_dir)):
            img = {'object': list()}

            try:
                tree = ET.parse(os.path.join(ann_dir, ann))
            except Exception as e:
                print('-+'*20)
                print(e)
                traceback.print_exc()
                print('Ignore this bad annotation: ' + os.path.join(ann_dir, ann))
                print('+-'*20)
                continue
            
            for elem in tree.iter():
                if 'filename' in elem.tag:
                    img['filename'] = os.path.join(img_dir, elem.text)
                    if '\t' in  img['filename']:
                        print('#'*20+ '\n\n\t' +img['filename'] + '\n\t' + elem.text + '\n\n' + '#' * 20)
                        print(type(elem.text))
                        print(elem.text.count('\t'))
                        print(elem.text.count(' '))
                if 'width' in elem.tag:
                    img['width'] = int(elem.text)
                if 'height' in elem.tag:
                    img['height'] = int(elem.text)
                if 'object' in elem.tag or 'part' in elem.tag:
                    obj = {}
                    
                    for attr in list(elem):
                        if 'name' in attr.tag:
                            obj['name'] = attr.text

                            if obj['name'] in seen_labels:
                                seen_labels[obj['name']] += 1
                            else:
                                seen_labels[obj['name']] = 1
                            
                            if len(labels) > 0 and obj['name'] not in labels:
                                break
                            else:
                                img['object'] += [obj]
                                
                        if 'bndbox' in attr.tag:
                            for dim in list(attr):
                                if 'xmin' in dim.tag:
                                    obj['xmin'] = int(round(float(dim.text)))
                                if 'ymin' in dim.tag:
                                    obj['ymin'] = int(round(float(dim.text)))
                                if 'xmax' in dim.tag:
                                    obj['xmax'] = int(round(float(dim.text)))
                                if 'ymax' in dim.tag:
                                    obj['ymax'] = int(round(float(dim.text)))

            if len(img['object']) > 0:
                all_insts += [img]
            else:
                print('Annotation without object: ', ann)

        cache = {'all_insts': all_insts, 'seen_labels': seen_labels}
        with open(cache_name, 'wb') as handle:
            pickle.dump(cache, handle, protocol=pickle.HIGHEST_PROTOCOL)    

    print('END annotations read:  ', len(all_insts))
    return all_insts, seen_labels
