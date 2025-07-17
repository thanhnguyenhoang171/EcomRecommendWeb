<h1> Web Bán Điện Thoại Di Động - Hệ thống gợi ý sản phẩm (Collaborative Filtering)</h1>
<h3>Trang Web bán hàng</h3>
<p> Web được xây dựng bằng Django, HTML, CSS, JS, Boostrap, MySQL</p>
<p>Trang web cung cấp cho người dùng các sản phẩm điện tử từ nhiều thương hiệu khác nhau (Samsung, iPhone, ...), khách hàng có thể bỏ sản phẩm vào giỏ hàng, thanh toán, tìm kiếm, lọc sản phẩm, để lại nhận xét và đánh giá (Rating).</p>
<h4>EER Diagram</h4>
<img src="https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/EER_Diagram.png"/>
<h4>Demo giao diện</h4>
<ol>
    <li> <p>Trang Chủ</p> <br> <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/home.png"/></li>
    <li>  <p>Trang đăng ký tài khoản User</p> <br> <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/register.png"/></li>
    <li>  <p>Trang đăng nhập</p> <br> <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/login.png"/></li>
    <li> <p>Trang thông tin của User (bao gồm thông tin địa chỉ giao hàng và chi tiết đơn hàng)</p> <br> <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/info.png"/> </li>
    <li> <p>Trang chi tiết về sản phẩm</p> <br> <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/detail_1.png"/>
    <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/detail_2.png"/> 
         <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/detail_3.png"/> 
    </li>
      <li>  <p>Trang tìm kiếm</p> <br> <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/search.png"/></li>
     <li>  <p>Trang giỏ hàng</p> <br> <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/cart.png"/></li>
      <li>  <p>Trang thanh toán</p> <br> <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/checkout.png"/></li>
      <li>  <p>Trang giới thiệu</p> <br> <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/about.png"/></li>
      <li>  <p>Trang liên hệ</p> <br> <img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/contact.png"/></li>
</ol>
<h3>Hệ thống gợi ý sản phẩm (Collaborative Filtering)</h3>
<p>Trong trang chi tiết sản phẩm, người dùng (User) sẽ được hệ thống gợi ý sản phẩm (Product) dựa trên mô hình lọc công như _Hình 1_ dựa trên những đánh giá (Rating) từ những người dùng khác _Hình 2_ có sự tương quan</p>
<figure>
    <img style="width:100%; height:100%;" src="https://raw.githubusercontent.com/thanhnguyenhoang171/EcomRecommendWeb/main/DemoPics/detail_2.png" alt="Detail Image" style="width:300px;">
    <figcaption>Hình 1. Hệ thống gợi ý sản phẩm cho người dùng</figcaption>
     <img style="width:100%; height:100%;" src="https://raw.githubusercontent.com/thanhnguyenhoang171/EcomRecommendWeb/main/DemoPics/detail_3.png" alt="Detail Image" style="width:300px;">
    <figcaption>Hình 2. Đánh giá sản phẩm</figcaption>
</figure>
<h3>Evalute</h3>
<p>Dự án đang ở giai đoạn hoàn thiện cơ bản, nên hệ số Sai số chuẩn (Standard Error - SE) và Sai số căn bậc hai của trung bình (Root Mean Square Error - RMSE) ở mức cao."</p>
<img src = "https://github.com/thanhnguyenhoang171/EcomRecommendWeb/blob/main/DemoPics/evaluate.png"/>
