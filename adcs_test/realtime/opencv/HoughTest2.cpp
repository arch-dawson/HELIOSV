#include <cv.h>
#include <cxcore.h>
#include <highgui.h>
#include <opencv2/imgproc/imgproc.hpp>

#include <iostream>
#include <fstream>
#include <time.h>

using namespace cv;
using namespace std;

int main(){
  ofstream timeFile;
  timeFile.open("/home/pi/outFile.txt");//, ios::app);
  timeFile << "Computation Time Over 50 Runs\n";

  Mat src = imread("/home/pi/sun4.png");
  Mat srcGray;

  clock_t t = clock();

  cvtColor(src, srcGray, CV_BGR2GRAY);
  
  //for(int i=0; i<50; i++){
    t = clock();
    vector<Vec3f> circles;
    HoughCircles(srcGray, circles, CV_HOUGH_GRADIENT, 1, srcGray.rows/8, 50, 30, 0, 0);
    
    for(size_t i=0; i< circles.size(); i++){
      Point center(cvRound(circles[i][0]), cvRound(circles[i][1]));
      timeFile << "Circle " << i << "\tx: " << center.x << "\ty: " << center.y << endl;
      int radius = cvRound(circles[i][2]);
      //circle center
      circle(src, center, 3, Scalar(0, 255, 0), -1, 8, 0);
      //circle outline
      circle(src, center, radius, Scalar(0,0,255), 3, 8, 0);
    }
    t = clock() - t;  

    //imwrite("/home/pi/sunOutput.jpg", src);

    //timeFile << "Computation Time:\n";
    timeFile << "\n";
    timeFile << ((float)t) / CLOCKS_PER_SEC;
    timeFile << " s";
    //timeFile.close();
  //}
  timeFile.close();
  return 0;
}
