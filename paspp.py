# -*- coding: utf-8 -*-
"""PASPP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ps8JPX8OwQqo0NTsEXP46n5s0DeN7GMV
"""

class PASPP(nn.Module):
    def __init__(self, inplanes, outplanes, output_stride=4, BatchNorm=nn.BatchNorm2d):
        super().__init__()
        if output_stride == 4:
            dilations = [1, 6, 12, 18]
        elif output_stride == 8:
            dilations = [1, 4, 6, 10]
        elif output_stride == 2:
            dilations = [1, 12, 24, 36]
        elif output_stride == 16:
            dilations = [1, 2, 3, 4]
        elif output_stride == 1:
            dilations = [1, 16, 32, 48]
        else:
            raise NotImplementedError
        self._norm_layer = BatchNorm
        self.silu = nn.SiLU(inplace=True)
        self.conv1 = self._make_layer(inplanes, outplanes // 4)
        self.conv2 = self._make_layer(inplanes, outplanes // 4)
        self.conv3 = self._make_layer(inplanes, outplanes // 4)
        self.conv4 = self._make_layer(inplanes, outplanes // 4)
        self.atrous_conv1 = nn.Conv2d(outplanes // 4, outplanes // 4, kernel_size=3, dilation=dilations[0], padding=dilations[0])
        self.atrous_conv2 = nn.Conv2d(outplanes // 4, outplanes // 4, kernel_size=3, dilation=dilations[1], padding=dilations[1])
        self.atrous_conv3 = nn.Conv2d(outplanes // 4, outplanes // 4, kernel_size=3, dilation=dilations[2], padding=dilations[2])
        self.atrous_conv4 = nn.Conv2d(outplanes // 4, outplanes // 4, kernel_size=3, dilation=dilations[3], padding=dilations[3])
        self.conv5 = self._make_layer(outplanes // 2, outplanes // 2)
        self.conv6 = self._make_layer(outplanes // 2, outplanes // 2)
        self.convout = self._make_layer(outplanes, outplanes)
        self._init_weight()

    def _make_layer(self, inplanes, outplanes):
        layer = []
        layer.append(nn.Conv2d(inplanes, outplanes, kernel_size = 1))
        layer.append(self._norm_layer(outplanes))
        layer.append(self.silu)
        return nn.Sequential(*layer)
    def forward(self, X):
        x1 = self.conv1(X)
        x2 = self.conv2(X)
        x3 = self.conv3(X)
        x4 = self.conv4(X)

        x12 = torch.add(x1, x2)
        x34 = torch.add(x3, x4)

        x1 = torch.add(self.atrous_conv1(x1),x12)
        x2 = torch.add(self.atrous_conv2(x2),x12)
        x3 = torch.add(self.atrous_conv3(x3),x34)
        x4 = torch.add(self.atrous_conv4(x4),x34)

        x12 = torch.cat([x1, x2], dim = 1)
        x34 = torch.cat([x3, x4], dim = 1)

        x12 = self.conv5(x12)
        x34 = self.conv5(x34)
        x = torch.cat([x12, x34], dim=1)
        x = self.convout(x)
        return x
    def _init_weight(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                torch.nn.init.kaiming_normal_(m.weight)
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()