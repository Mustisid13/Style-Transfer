from flask import Flask,render_template,request,send_file,jsonify
import torch 
from torchvision import transforms , models 
from PIL import Image 
import numpy as np
import io



device = ("cuda" if torch.cuda.is_available() else "cpu")
transform = transforms.Compose([transforms.Resize(350),
                              transforms.ToTensor(),
                              transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))])


model = models.vgg19(pretrained=True).features
for p in model.parameters():
    p.requires_grad = False
model.to(device)


def model_activations(input,model):
    layers = {
    '0' : 'conv1_1',
    '5' : 'conv2_1',
    '10': 'conv3_1',
    '19': 'conv4_1',
    '21': 'conv4_2',
    '28': 'conv5_1'
    }
    features = {}
    x = input
    x = x.unsqueeze(0)
    for name,layer in model._modules.items():
        x = layer(x)
        if name in layers:
            features[layers[name]] = x 
    
    return features


def imcnvt(image):
    x = image.to("cpu").clone().detach().numpy().squeeze()
    x = x.transpose(1,2,0)
    x = x*np.array((0.5,0.5,0.5)) + np.array((0.5,0.5,0.5))
    return x

def gram_matrix(imgfeature):
    _,d,h,w = imgfeature.size()
    imgfeature = imgfeature.view(d,h*w)
    gram_mat = torch.mm(imgfeature,imgfeature.t())
    
    return gram_mat


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/style',methods=['POST'])
def style_transfer():
    import gc
    gc.collect()
    content_image = io.BytesIO(request.files['img1'].read())
    style_image = io.BytesIO(request.files['img2'].read())
    
    content = Image.open(content_image).convert('RGB')
    content.save('mm.jpeg')
    content = transform(content).to(device)
    print("COntent shape => ", content.shape)
    style = Image.open(style_image).convert('RGB')
    style = transform(style).to(device)

    target = content.clone().requires_grad_(True).to(device)

    style_features = model_activations(style,model)
    content_features = model_activations(content,model)

    style_wt_meas = {"conv1_1" : 1.0, 
                    "conv2_1" : 0.8,
                    "conv3_1" : 0.4,
                    "conv4_1" : 0.2,
                    "conv5_1" : 0.1}

    style_grams = {layer:gram_matrix(style_features[layer]) for layer in style_features}

    content_wt = 100
    style_wt = 1e8

    # print_after = 500
    epochs = 200 #chnage to 200
    optimizer = torch.optim.Adam([target],lr=0.007)

    for i in range(1,epochs+1):
        target_features = model_activations(target,model)
        content_loss = torch.mean((content_features['conv4_2']-target_features['conv4_2'])**2)

        style_loss = 0
        for layer in style_wt_meas:
            style_gram = style_grams[layer]
            target_gram = target_features[layer]
            _,d,w,h = target_gram.shape
            target_gram = gram_matrix(target_gram)

            style_loss += (style_wt_meas[layer]*torch.mean((target_gram-style_gram)**2))/d*w*h
        
        total_loss = content_wt*content_loss + style_wt*style_loss 
        
        if i%10==0:       
            print("epoch ",i," ", total_loss)
        
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()

    mean=[0.485, 0.456, 0.406]
    # std=[0.229, 0.224, 0.225]
    std =[0.24,0.22,0.25]
    x = target.to('cpu').detach()
    z = x * torch.tensor(std).view(3, 1, 1)
    z = z + torch.tensor(mean).view(3, 1, 1)
    img2 = transforms.ToPILImage(mode='RGB')(z)
    file_obj = io.BytesIO()
    
    img2.save(file_obj,"JPEG")
    file_obj.seek(0)

    return send_file(file_obj,mimetype='image/jpeg')
    
       
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
