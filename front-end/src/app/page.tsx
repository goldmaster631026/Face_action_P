"use client";
// import Image from "next/image";
// import { useEffect, useInsertionEffect, useState } from "react";
// import api from '../service/axios'
// import { cookies } from "next/headers";
// export default function Home() {
//   const [videoURL, setVideoUrl] = useState<string>();
//   const [uploadVideo, setUploadVideo] = useState<any>(null)
//   const [link, setUploadlink] = useState<any>()
//   const [uploadState, setupLoadState] = useState<string>()


//   const SendVideo = () => {
//     const formData = new FormData()
//     formData.append('video', uploadVideo)
//     console.log("UploadI:", uploadVideo)
//     api.post('/facial_emotion', formData, {
//       headers: {
//         'Content-Type': 'multipart/form-data'
//       }
//     })
//     // api.post('/facial_emotion', { data: "hello" })
//       .then((res) => {
//         console.log(res.data)
//         // const jsonData = JSON.stringify(res.data);
//         // const blob = new Blob([jsonData], { type: 'application/json' });
//         // const url = URL.createObjectURL(blob);
//         // const a = document.createElement('a');
//         // a.href = url;
//         // a.download = 'data.json';
//         // a.click();
//       })
//   }

//   const SendLink = () => {
//     api.post('/facial_emotion', { videoLink: link, uploadState: uploadState })
//       .then((res) => {
//         console.log(res.data)
//       })
//   }

//   const SendSource = () => {
//     if (uploadState === 'video') {
//       console.log("Video is sending!!!")
//       SendVideo()
//     }
//     else if (uploadState === 'link') {
//       console.log("Link is sending!!!")
//       SendLink()
//     }
//   }

//   useEffect(() => {
//     console.log(uploadState)
//   }, [uploadState])

//   return (
//     <div className="flex flex-col justify-center items-center w-[100vw] h-[100vh]">
//       <input type="file" className=""
//         onChange={(e: any) => {
//           setVideoUrl(URL.createObjectURL(e.target.files[0]))
//           console.log(URL.createObjectURL(e.target.files[0]))
//           setUploadVideo(e.target.files[0])
//           setupLoadState('video')


//         }}
//       />
//       <video className="w-[10%] h-[10%] mt-[100px] bg-red-100" src={videoURL} controls></video>
//       <input type="text" className=""
//         onChange={(e: any) => {
//           setUploadlink(e.target.value)
//           console.log(link)
//           setupLoadState('link')
//         }}
//       />
//       <button className="w-[400px] h-[50px] bg-red-300 mt-[100px]"
//         onClick={() => {
//           SendSource()
//         }}>Sender</button>
//     </div>
//   );
// }


import Image from "next/image";
import { useEffect, useState } from "react";
import api from '../service/axios';

export default function Home() {
  const [videoURL, setVideoUrl] = useState<string>();
  const [uploadVideo, setUploadVideo] = useState<any>(null);
  const [link, setUploadlink] = useState<string>('');
  const [uploadState, setupLoadState] = useState<string>('');

  const SendVideo = () => {
    const formData = new FormData();
    formData.append('video', uploadVideo);

    api.post('/facial_emotion_video', formData, {
      params:{
        uploadState: uploadState
      },
      headers: {
      
        'Content-Type': 'multipart/form-data'
      }
    })
    .then((res) => {
      // console.log("Video : ", res.data);
      console.log("Video : ", res.data)
        const jsonData = JSON.stringify(res.data);
        const blob = new Blob([jsonData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'data.json';
        a.click();
    })
    .catch((error) => {
      console.error(error);
    });
  }

// query = {'lat':'45', 'lon':'180'}
// response = requests.get('http://api.open-notify.org/iss-pass.json', params=query)
// print(response.json())



  const SendLink = () => {
    api.post('/facial_emotion_link', 
    { videoLink: link, 
      uploadState: uploadState 
    })

    private_url_response = requests.get(
      url=private_url,
      auth=HTTPBasicAuth(github_username, token)
  )

    .then((res) => {
     
      console.log("Link : ", res.data)
        const jsonData = JSON.stringify(res.data);
        const blob = new Blob([jsonData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'data.json';
        a.click();

      // return res.data

    })
    .catch((error) => {
      console.error(error);
    });
  }

  const SendSource = () => {
    if (uploadState === 'video') {
      SendVideo();
    } else if (uploadState === 'link') {
      SendLink();
    }
  }

  useEffect(() => {
    console.log(uploadState);
  }, [uploadState]);

  return (
    <div className="flex flex-col justify-center items-center w-[100vw] h-[100vh]">
      <input type="file" className=""
        onChange={(e: any) => {
          setVideoUrl(URL.createObjectURL(e.target.files[0]));
          setUploadVideo(e.target.files[0]);
          setupLoadState('video');
        }}
      />
      <video className="w-[10%] h-[10%] mt-[100px] bg-red-100" src={videoURL} controls></video>
      <input type="text" className=""
        value={link}
        onChange={(e: any) => {
          setUploadlink(e.target.value);
          setupLoadState('link');
        }}
      />
      <button className="w-[400px] h-[50px] bg-red-300 mt-[100px]"
        onClick={SendSource}>Sender</button>
    </div>
  );
}
