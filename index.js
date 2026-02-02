// ハンバーガーメニュー
const hamburger = document.getElementById("hamburger");
const navLinks = document.getElementById("navLinks");

hamburger.addEventListener("click", () => {
  navLinks.classList.toggle("active");
});

// メニューリンクをクリックしたらメニューを閉じる
document.querySelectorAll(".nav-links a").forEach((link) => {
  link.addEventListener("click", () => {
    navLinks.classList.remove("active");
  });
});

// スクロールアニメーション
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -100px 0px",
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("fade-in");
    }
  });
}, observerOptions);

// すべてのセクションを監視
document.querySelectorAll("section").forEach((section) => {
  observer.observe(section);
});

// スムーススクロール
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

// 価格データ
const priceData = {
  "esl-light": {
    name: "ESL Light course",
    description:
      "2025年8月24日以降に留学を開始される方が対象の新コースです。マンツーマン(50分×3)とグループ(50分×1)で構成されています。",
    isNew: true,
    prices: {
      single: {
        1: 47125,
        2: 94250,
        3: 130500,
        4: 145000,
        8: 290000,
        12: 431000,
        16: 574000,
        20: 717000,
        24: 860000,
      },
      double: {
        1: 40625,
        2: 81250,
        3: 112500,
        4: 125000,
        8: 250000,
        12: 371000,
        16: 494000,
        20: 617000,
        24: 740000,
      },
      triple: {
        1: 37375,
        2: 74750,
        3: 103500,
        4: 115000,
        8: 230000,
        12: 341000,
        16: 454000,
        20: 567000,
        24: 680000,
      },
    },
  },
  "esl-a": {
    name: "ESL A course",
    description:
      "マンツーマン(50分×5)とグループ(50分×1)で英語力を総合的に伸ばすコースです。",
    isNew: false,
    prices: {
      single: {
        1: 56875,
        2: 105000,
        3: 144375,
        4: 175000,
        8: 350000,
        12: 521000,
        16: 694000,
        20: 867000,
        24: 1040000,
      },
      double: {
        1: 50375,
        2: 93000,
        3: 127875,
        4: 155000,
        8: 310000,
        12: 461000,
        16: 614000,
        20: 767000,
        24: 920000,
      },
      triple: {
        1: 47125,
        2: 87000,
        3: 119625,
        4: 145000,
        8: 290000,
        12: 431000,
        16: 574000,
        20: 717000,
        24: 860000,
      },
    },
  },
  "esl-b": {
    name: "ESL B course",
    description:
      "マンツーマン(50分×6)とグループ(50分×1)でより集中的に学習するコースです。",
    isNew: false,
    prices: {
      single: {
        1: 61100,
        2: 112800,
        3: 155100,
        4: 188000,
        8: 376000,
        12: 560000,
        16: 746000,
        20: 932000,
        24: 1118000,
      },
      double: {
        1: 54600,
        2: 100800,
        3: 138600,
        4: 168000,
        8: 336000,
        12: 500000,
        16: 666000,
        20: 832000,
        24: 998000,
      },
      triple: {
        1: 51350,
        2: 94800,
        3: 130350,
        4: 158000,
        8: 316000,
        12: 470000,
        16: 626000,
        20: 782000,
        24: 938000,
      },
    },
  },
  "esl-c": {
    name: "ESL C course",
    description:
      "マンツーマン(50分×7)とグループ(50分×1)で徹底的に英語力を鍛えるコースです。",
    isNew: false,
    prices: {
      single: {
        1: 65325,
        2: 120600,
        3: 165825,
        4: 201000,
        8: 402000,
        12: 599000,
        16: 798000,
        20: 997000,
        24: 1196000,
      },
      double: {
        1: 58825,
        2: 108600,
        3: 149325,
        4: 181000,
        8: 362000,
        12: 539000,
        16: 718000,
        20: 897000,
        24: 1076000,
      },
      triple: {
        1: 55575,
        2: 102600,
        3: 141075,
        4: 171000,
        8: 342000,
        12: 509000,
        16: 678000,
        20: 847000,
        24: 1016000,
      },
    },
  },
  "esl-d": {
    name: "ESL D course",
    description:
      "マンツーマン(50分×8)で完全にカスタマイズされた学習が可能なコースです。",
    isNew: false,
    prices: {
      single: {
        1: 68250,
        2: 136500,
        3: 189000,
        4: 210000,
        8: 420000,
        12: 626000,
        16: 834000,
        20: 1042000,
        24: 1250000,
      },
      double: {
        1: 61750,
        2: 123500,
        3: 171000,
        4: 190000,
        8: 380000,
        12: 566000,
        16: 754000,
        20: 942000,
        24: 1130000,
      },
      triple: {
        1: 58500,
        2: 117000,
        3: 162000,
        4: 180000,
        8: 360000,
        12: 536000,
        16: 714000,
        20: 892000,
        24: 1070000,
      },
    },
  },
  "test-a": {
    name: "IELTS/TOEIC A course",
    description:
      "マンツーマン(50分×5)とグループ(50分×1)で試験対策に特化したコースです。優秀な試験対策専門の選抜チームが担当します。",
    isNew: false,
    prices: {
      single: {
        1: 61100,
        2: 112800,
        3: 155100,
        4: 188000,
        8: 376000,
        12: 560000,
        16: 746000,
        20: 932000,
        24: 1118000,
      },
      double: {
        1: 54600,
        2: 100800,
        3: 138600,
        4: 168000,
        8: 336000,
        12: 500000,
        16: 666000,
        20: 832000,
        24: 998000,
      },
      triple: {
        1: 51350,
        2: 94800,
        3: 130350,
        4: 158000,
        8: 316000,
        12: 470000,
        16: 626000,
        20: 782000,
        24: 938000,
      },
    },
  },
  "test-b": {
    name: "IELTS/TOEIC B course",
    description:
      "マンツーマン(50分×6)とグループ(50分×1)で試験対策に特化したコースです。",
    isNew: false,
    prices: {
      single: {
        1: 65325,
        2: 120600,
        3: 165825,
        4: 201000,
        8: 402000,
        12: 599000,
        16: 798000,
        20: 997000,
        24: 1196000,
      },
      double: {
        1: 58825,
        2: 108600,
        3: 149325,
        4: 181000,
        8: 362000,
        12: 539000,
        16: 718000,
        20: 897000,
        24: 1076000,
      },
      triple: {
        1: 55575,
        2: 102600,
        3: 141075,
        4: 171000,
        8: 342000,
        12: 509000,
        16: 678000,
        20: 847000,
        24: 1016000,
      },
    },
  },
  "test-c": {
    name: "IELTS/TOEIC C course",
    description:
      "マンツーマン(50分×7)とグループ(50分×1)で試験対策に特化したコースです。",
    isNew: false,
    prices: {
      single: {
        1: 69550,
        2: 128400,
        3: 176550,
        4: 214000,
        8: 428000,
        12: 638000,
        16: 850000,
        20: 1062000,
        24: 1274000,
      },
      double: {
        1: 63050,
        2: 116400,
        3: 160050,
        4: 194000,
        8: 388000,
        12: 578000,
        16: 770000,
        20: 962000,
        24: 1154000,
      },
      triple: {
        1: 59800,
        2: 110400,
        3: 151800,
        4: 184000,
        8: 368000,
        12: 548000,
        16: 730000,
        20: 912000,
        24: 1094000,
      },
    },
  },
  "test-d": {
    name: "IELTS/TOEIC D course",
    description: "マンツーマン(50分×8)で試験対策に特化したコースです。",
    isNew: false,
    prices: {
      single: {
        1: 72475,
        2: 144950,
        3: 200700,
        4: 223000,
        8: 446000,
        12: 665000,
        16: 886000,
        20: 1107000,
        24: 1328000,
      },
      double: {
        1: 65975,
        2: 131950,
        3: 182700,
        4: 203000,
        8: 406000,
        12: 605000,
        16: 806000,
        20: 1007000,
        24: 1208000,
      },
      triple: {
        1: 62725,
        2: 125450,
        3: 173700,
        4: 193000,
        8: 386000,
        12: 575000,
        16: 766000,
        20: 957000,
        24: 1148000,
      },
    },
  },
};

// 価格計算機能
const courseSelect = document.getElementById("courseSelect");
const roomSelect = document.getElementById("roomSelect");
const periodSelect = document.getElementById("periodSelect");
const priceResult = document.getElementById("priceResult");
const priceAmount = document.getElementById("priceAmount");
const courseDescription = document.getElementById("courseDescription");

function calculatePrice() {
  const course = courseSelect.value;
  const room = roomSelect.value;
  const period = periodSelect.value;

  if (course && room && period) {
    const courseData = priceData[course];
    const price = courseData.prices[room][period];

    // 価格を表示
    priceAmount.textContent = "¥" + price.toLocaleString();

    // コース説明を表示
    let descriptionHTML = "";
    if (courseData.isNew) {
      descriptionHTML += '<span class="new-badge">新コース</span><br>';
    }
    descriptionHTML +=
      "<strong>" + courseData.name + "</strong><br>" + courseData.description;
    courseDescription.innerHTML = descriptionHTML;

    // 結果を表示
    priceResult.classList.remove("hidden");

    // スムーズにスクロール
    setTimeout(() => {
      priceResult.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 100);
  }
}

// イベントリスナーを追加
courseSelect.addEventListener("change", calculatePrice);
roomSelect.addEventListener("change", calculatePrice);
periodSelect.addEventListener("change", calculatePrice);

// ヒーロースライドショー
const heroSlideshow = document.getElementById("heroSlideshow");

// 固定ファイル名の画像を取得
async function getImageFiles() {
  const imageFiles = [];

  // slide_1.jpg から slide_5.jpg まで順番にチェック
  for (let i = 1; i <= 5; i++) {
    const imagePath = `images/facebook/slide_${i}.jpg`;
    try {
      const response = await fetch(imagePath, { method: "HEAD" });
      if (response.ok) {
        imageFiles.push(imagePath);
      }
    } catch (error) {
      console.log(`画像が見つかりません: slide_${i}.jpg`);
    }
  }

  return imageFiles;
}

let currentSlide = 0;

// スライド要素を生成
function createSlides(imageFiles) {
  // 既存のスライドをクリア
  heroSlideshow.innerHTML = "";

  imageFiles.forEach((imagePath, index) => {
    const slide = document.createElement("div");
    slide.className = "hero-slide";
    slide.style.backgroundImage = `url('${imagePath}')`;
    if (index === 0) {
      slide.classList.add("active");
    }
    heroSlideshow.appendChild(slide);
  });
}

// スライドを切り替え
function nextSlide() {
  const slides = document.querySelectorAll(".hero-slide");
  slides[currentSlide].classList.remove("active");
  currentSlide = (currentSlide + 1) % slides.length;
  slides[currentSlide].classList.add("active");
}

// スライドショーを開始
async function startSlideshow() {
  try {
    const imageFiles = await getImageFiles();
    console.log(`見つかった画像: ${imageFiles.length}枚`);

    if (imageFiles.length > 0) {
      createSlides(imageFiles);
      setInterval(nextSlide, 3000); // 3秒間隔で切り替え
    } else {
      console.log("画像が見つかりませんでした");
      // フォールバック: デフォルト画像またはメッセージを表示
      heroSlideshow.innerHTML =
        '<div class="hero-slide active" style="background-color: #f0f0f0; display: flex; align-items: center; justify-content: center;"><p style="color: #666; font-size: 1.2rem;">画像を読み込み中...</p></div>';
    }
  } catch (error) {
    console.error("スライドショーの初期化に失敗:", error);
    // エラー時のフォールバック
    heroSlideshow.innerHTML =
      '<div class="hero-slide active" style="background-color: #f0f0f0; display: flex; align-items: center; justify-content: center;"><p style="color: #666; font-size: 1.2rem;">画像の読み込みに失敗しました</p></div>';
  }
}

// ページ読み込み完了後にスライドショーを開始
document.addEventListener("DOMContentLoaded", startSlideshow);

const postDiv = document.querySelector(".voices-grid");
const personData = async function () {
  try {
    const log = await fetch("contents/person.json");
    const responses = await log.json();

    if (!postDiv) {
      console.error('voices-gridが見つかりません');
      return;
    }

    let html = '';
    for (const response of responses) {
      console.log(response);
      html += `
        <div class="voice-card">
          <div class="voice-image-container">
          <a href="${response.url}">
            ${
              response.img
                ? `<img src="${response.img}" alt="${response.name}" class="voice-image">`
                : '<div class="voice-image" style="background-color: #ddd;"></div>'
            }
            
            <div class="voice-info">
              <div class="name">${response.name}</div>
              <div class="details">年齢：${response.age}<br>留学期間：${
        response.period
      }</div>
            </div>
            </a>
          </div>
          <div class="advice">
            ${response.advice}
          </div>
          <a href="${
            response.url
          }" class="read-more">続きを読む <span>›</span></a>
        </div>
      `;
    }
    postDiv.innerHTML = html;
    console.log(`✅ ${responses.length}件の体験談を読み込みました`);
  } catch (error) {
    console.error('❌ データ読み込みエラー:', error);
  }
};
personData();

// ジプニーモーダル
const jeepneyModal = document.getElementById("jeepneyModal");
const openJeepneyModal = document.getElementById("openJeepneyModal");
const closeJeepneyModal = document.getElementById("closeJeepneyModal");

openJeepneyModal.addEventListener("click", (e) => {
  e.preventDefault();
  jeepneyModal.classList.add("active");
  document.body.style.overflow = "hidden";
});

closeJeepneyModal.addEventListener("click", () => {
  jeepneyModal.classList.remove("active");
  document.body.style.overflow = "";
});

jeepneyModal.addEventListener("click", (e) => {
  if (e.target === jeepneyModal) {
    jeepneyModal.classList.remove("active");
    document.body.style.overflow = "";
  }
});

// 観光地モーダル
const touristModal = document.getElementById("touristModal");
const openTouristModal = document.getElementById("openTouristModal");
const closeTouristModal = document.getElementById("closeTouristModal");

openTouristModal.addEventListener("click", (e) => {
  e.preventDefault();
  touristModal.classList.add("active");
  document.body.style.overflow = "hidden";
});

closeTouristModal.addEventListener("click", () => {
  touristModal.classList.remove("active");
  document.body.style.overflow = "";
});

touristModal.addEventListener("click", (e) => {
  if (e.target === touristModal) {
    touristModal.classList.remove("active");
    document.body.style.overflow = "";
  }
});

// Reviews toggle (Bootstrap collapse)
const reviewsToggle = document.getElementById("reviewsToggle");
const reviewsHidden = document.getElementById("reviewsHidden");

reviewsHidden.addEventListener("shown.bs.collapse", () => {
  reviewsToggle.innerHTML = 'CLOSE <span class="reviews-toggle-icon">&#9662;</span>';
});

reviewsHidden.addEventListener("hidden.bs.collapse", () => {
  reviewsToggle.innerHTML = 'VIEW MORE <span class="reviews-toggle-icon">&#9662;</span>';
});

const swiper = new Swiper(".gallery-slider", {
  autoplay: {
    delay: 0,
    disableOnInteraction: false,
  },
  loop: true,
  speed: 10000,
  slidesPerView: "auto",
  spaceBetween: 16,
  freeMode: true,
  freeModeMomentum: false,
});

const swiper2 = new Swiper(".gallery-slider-reverse", {
  autoplay: {
    delay: 0,
    disableOnInteraction: false,
    reverseDirection: true,
  },
  loop: true,
  speed: 8000,
  slidesPerView: "auto",
  spaceBetween: 16,
  freeMode: true,
  freeModeMomentum: false,
});
